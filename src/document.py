"""DOCX document conversion helpers.

Word is the only backend used for PDF -> DOCX. LibreOffice is a fallback for
DOCX -> PDF when Word is unavailable. The caller owns the final destination;
this module only writes the supplied temporary path.
"""
from i18n import tr
from pathlib import Path
import os
import ctypes
from ctypes import wintypes
import json
import posixpath
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

try:
    import winreg
except ImportError:  # pragma: no cover - allows engine tests off Windows
    winreg = None

FLAGS = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
TIMEOUT = 120
WORD_NS = {'http://schemas.openxmlformats.org/wordprocessingml/2006/main', 'http://purl.oclc.org/ooxml/wordprocessingml/main'}
DOCX_TYPE = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml'


def quality_note(extension, fmt):
    pair = (extension.lower().lstrip('.'), fmt.lower().lstrip('.'))
    if pair == ('pdf', 'docx'):
        return tr('표·배치가 달라질 수 있으며 이미지 중심 문서는 텍스트를 편집할 수 없을 수 있습니다. OCR은 지원하지 않습니다.')
    if pair == ('docx', 'pdf'):
        return tr('글꼴·배치가 달라질 수 있습니다. Word 편집 기능과 주석·변경 추적 표시는 PDF에 보존되지 않습니다.')
    return ''


def _word_installed():
    if winreg is None:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'Word.Application\CLSID'):
            return True
    except OSError:
        return False


def _libreoffice_path():
    candidates = [shutil.which('soffice')]
    for base in ('PROGRAMFILES', 'PROGRAMFILES(X86)'):
        candidates.append(str(Path(os.environ.get(base, 'C:/Program Files')) / 'LibreOffice/program/soffice.exe'))
    return next((candidate for candidate in candidates if candidate and Path(candidate).is_file()), None)


def backend(direction):
    """Return the first usable backend for a conversion direction."""
    if direction not in {'pdf-to-docx', 'docx-to-pdf'}:
        raise ValueError(tr('이 파일에서 지원하지 않는 변환입니다.'))
    if direction == 'pdf-to-docx':
        return 'Built-in PDF extraction', None
    if _word_installed():
        return 'Word', None
    libreoffice = _libreoffice_path()
    return ('LibreOffice', libreoffice) if libreoffice else (None, None)


def validate_docx(path):
    """Validate the package and return whether its body contains text/objects."""
    try:
        with zipfile.ZipFile(path) as package:
            if package.testzip() is not None:
                raise ValueError
            types = ET.fromstring(package.read('[Content_Types].xml'))
            rels = ET.fromstring(package.read('_rels/.rels'))
            main = next(r for r in rels if r.get('Type', '').endswith('/officeDocument') and r.get('TargetMode') != 'External')
            target = main.attrib['Target'].lstrip('/')
            if '\\' in target or '..' in target.split('/'):
                raise ValueError
            target = posixpath.normpath(target)
            if not any(t.get('PartName') == '/' + target and t.get('ContentType') == DOCX_TYPE for t in types):
                raise ValueError
            doc = ET.fromstring(package.read(target))
            if doc.tag not in {'{' + ns + '}document' for ns in WORD_NS}:
                raise ValueError
            body = next((child for child in doc if child.tag in {'{' + ns + '}body' for ns in WORD_NS}), None)
            if body is None:
                raise ValueError
            has_text = any(e.tag.rsplit('}', 1)[-1] == 't' and (e.text or '').strip() for e in body.iter())
            has_objects = any(e.tag.rsplit('}', 1)[-1] in {'drawing', 'pict', 'object', 'altChunk'} for e in body.iter())
            return {'text': has_text, 'objects': has_objects}
    except (OSError, zipfile.BadZipFile, ValueError, KeyError, StopIteration, ET.ParseError, RuntimeError) as exc:
        raise ValueError(tr('DOCX 문서를 읽을 수 없습니다. 암호를 해제하고 파일의 손상 여부를 확인해 주세요.')) from exc


def _stop_owned_word(owner_file):
    """Terminate only the helper's newly-created Word instance, with PID reuse protection."""
    try:
        owner = json.loads(owner_file.read_text(encoding='utf-8-sig'))
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
        kernel.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x1000 | 0x0001, False, int(owner['pid']))
        if not handle:
            return
        try:
            times = [wintypes.FILETIME() for _ in range(4)]
            if kernel.GetProcessTimes(handle, *(ctypes.byref(t) for t in times)):
                created = (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime
                if created == int(owner['created']):
                    kernel.TerminateProcess(handle, 1)
        finally:
            kernel.CloseHandle(handle)
    except (OSError, ValueError, KeyError):
        pass


def _script_path():
    root = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
    path = root / 'source' / 'word.ps1'
    return path if path.exists() else Path(__file__).with_name('word.ps1')


def _run_word(src, dst, direction, cancel):
    from engine import check, Cancelled
    powershell = Path(os.environ.get('SYSTEMROOT', 'C:/Windows')) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
    args = [str(powershell), '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', str(_script_path()),
            '-InputFile', str(Path(src).resolve()), '-OutputFile', str(Path(dst).resolve()), '-Direction', direction]
    with tempfile.TemporaryDirectory(prefix='sfc-word-') as temp, tempfile.TemporaryFile() as log:
        owner = Path(temp) / 'owner.json'
        stop = Path(temp) / 'cancel'
        args += ['-OwnerFile', str(owner), '-CancelFile', str(stop)]
        process = subprocess.Popen(args, stdout=log, stderr=log, creationflags=FLAGS)
        start = time.monotonic()
        try:
            while process.poll() is None:
                if cancel.wait(.1):
                    raise Cancelled()
                if time.monotonic() - start > TIMEOUT:
                    raise ValueError(tr('Office의 응답이 늦어지고 있습니다. 열린 대화상자를 확인한 뒤 다시 시도해 주세요.'))
            if process.returncode:
                log.seek(0)
                detail = log.read().decode('utf-8', errors='replace')[-1200:]
                raise ValueError(tr('Office에서 변환하지 못했습니다. 앱에서 파일이 열리는지 확인해 주세요.\n\n상세 오류: ') + detail)
            check(cancel)
        finally:
            if process.poll() is None:
                stop.touch()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    _stop_owned_word(owner)
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.kill()
            process.wait()
            _stop_owned_word(owner)


def _run_libreoffice(src, dst, exe, cancel):
    from engine import check, Cancelled
    with tempfile.TemporaryDirectory(prefix='sfc-writer-') as temp, tempfile.TemporaryFile() as log:
        root = Path(temp)
        args = [exe, '-env:UserInstallation=' + (root / 'profile').as_uri(), '--headless', '--convert-to',
                'pdf:writer_pdf_Export', '--outdir', str(root), str(Path(src).resolve())]
        process = subprocess.Popen(args, stdout=log, stderr=log, creationflags=FLAGS)
        start = time.monotonic()
        try:
            while process.poll() is None:
                if cancel.wait(.1):
                    raise Cancelled()
                if time.monotonic() - start > TIMEOUT:
                    raise ValueError(tr('Office의 응답이 늦어지고 있습니다. 열린 대화상자를 확인한 뒤 다시 시도해 주세요.'))
            log.seek(0)
            output = log.read()
        finally:
            if process.poll() is None:
                process.kill()
            process.wait()
        check(cancel)
        if process.returncode:
            detail = output.decode('utf-8', errors='replace')[-1200:]
            raise ValueError(tr('Office에서 변환하지 못했습니다. 앱에서 파일이 열리는지 확인해 주세요.\n\n상세 오류: ') + detail)
        result = root / (Path(src).stem + '.pdf')
        if result.exists():
            shutil.copy2(result, dst)


def _convert(src, dst, direction, cancel, progress):
    from engine import check
    name, executable = backend(direction)
    if not name:
        raise ValueError(tr('DOCX를 PDF로 변환하려면 Microsoft Word 또는 LibreOffice를 설치해 주세요.'))
    check(cancel)
    progress(tr('변환 중…'))
    if name == 'Word':
        _run_word(src, dst, direction, cancel)
    else:
        _run_libreoffice(src, dst, executable, cancel)
    check(cancel)
    if not Path(dst).is_file() or not Path(dst).stat().st_size:
        raise ValueError(tr('변환 결과를 만들지 못했습니다. 파일의 암호와 손상 여부, Office 상태를 확인해 주세요.'))


def docx_to_pdf(src, dst, cancel, progress=lambda text: None):
    validate_docx(src)
    _convert(src, dst, 'docx-to-pdf', cancel, progress)
    import pymupdf
    try:
        # A failed MuPDF file open can retain a Windows file handle in its
        # exception traceback. Read first so the staging directory stays removable.
        with pymupdf.open(stream=Path(dst).read_bytes(), filetype='pdf') as doc:
            if not len(doc):
                raise ValueError
    except Exception:
        raise ValueError(tr('PDF 결과에 페이지가 없습니다. 원본 파일을 확인해 주세요.'))


def _drawing_xml(rel_id, name, width_emu, height_emu, index):
    return f'''<w:p><w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{width_emu}" cy="{height_emu}"/><wp:docPr id="{index}" name="{escape(name)}"/><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="{index}" name="{escape(name)}"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="{rel_id}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{width_emu}" cy="{height_emu}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'''


def _pdf_to_docx_fallback(src, dst, cancel, progress):
    """Create an editable-text/image DOCX without an Office installation."""
    import pymupdf
    with pymupdf.open(src) as pdf:
        body = []
        media = []
        for page_index, page in enumerate(pdf):
            from engine import check
            check(cancel)
            progress(tr('PDF {v0}/{v1}페이지', v0=page_index + 1, v1=len(pdf)))
            text = page.get_text('text').replace('\x00', '').strip()
            if text:
                for line in text.splitlines():
                    body.append('<w:p><w:r><w:t xml:space="preserve">' + escape(line) + '</w:t></w:r></w:p>')
            else:
                pix = page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False)
                image_name = f'page-{page_index + 1:04d}.png'
                media.append((image_name, pix.tobytes('png'), pix.width, pix.height))
                width = 595 * 9525
                height = max(1, int(width * pix.height / pix.width))
                body.append(_drawing_xml(f'rId{len(media)}', image_name, width, height, page_index + 1))
            if page_index + 1 < len(pdf):
                body.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
    image_rels = ''.join(f'<Relationship Id="rId{i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{escape(name)}"/>' for i, (name, _, _, _) in enumerate(media))
    document = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body>''' + ''.join(body) + '<w:sectPr/></w:body></w:document>'
    rels = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rIdDoc" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>{image_rels}</Relationships>'''
    types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>'''
    root_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rIdDoc" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'''
    docx_rels = rels
    with zipfile.ZipFile(dst, 'w', compression=zipfile.ZIP_DEFLATED) as package:
        package.writestr('[Content_Types].xml', types)
        package.writestr('_rels/.rels', root_rels)
        package.writestr('word/document.xml', document)
        package.writestr('word/_rels/document.xml.rels', docx_rels)
        for name, data, _, _ in media:
            package.writestr('word/media/' + name, data)


def pdf_to_docx(src, dst, cancel, progress=lambda text: None):
    from engine import check
    import pymupdf
    source_has_content = False
    with pymupdf.open(src) as pdf:
        if pdf.needs_pass:
            raise ValueError(tr('PDF의 암호를 해제한 뒤 다시 시도해 주세요.'))
        if not len(pdf):
            raise ValueError(tr('페이지가 없는 PDF입니다.'))
        for page in pdf:
            check(cancel)
            if page.get_text().strip() or page.get_images() or page.get_drawings():
                source_has_content = True
                break
    # Word's PDF importer can block on a hidden conversion dialog. The built-in
    # extraction path is deterministic and works in portable installations.
    _pdf_to_docx_fallback(src, dst, cancel, progress)
    content = validate_docx(dst)
    if source_has_content and not any(content.values()):
        raise ValueError(tr('원본 내용이 DOCX 결과에 포함되지 않았습니다.'))
