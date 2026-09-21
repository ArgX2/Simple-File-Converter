"""Optional packaged-runtime smoke check: Simple File Converter.exe --self-test <report-folder>."""
import json
import threading
from pathlib import Path
from PIL import Image
from engine import convert, inspect, run_ffmpeg


def run_documents(folder):
    """Opt-in real Office smoke check, also runnable from the portable EXE."""
    import hashlib
    import zipfile
    import pymupdf
    from document import backend, validate_docx
    from version import VERSION
    folder = Path(folder).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    checks = []
    report = {'ok': False, 'version': VERSION, 'checks': checks,
              'docx_backend': backend('docx-to-pdf')[0], 'pdf_backend': backend('pdf-to-docx')[0]}
    try:
        source = folder / '문서 sample & (1).docx'
        ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        with zipfile.ZipFile(source, 'w') as package:
            package.writestr('[Content_Types].xml', '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
            package.writestr('_rels/.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
            package.writestr('word/document.xml', f'''<w:document xmlns:w="{ns}"><w:body>
                <w:p><w:r><w:rPr><w:rFonts w:ascii="Malgun Gothic" w:eastAsia="맑은 고딕"/></w:rPr><w:t>First page / 한글 문서 변환</w:t></w:r></w:p>
                <w:tbl><w:tblPr><w:tblW w:w="5000" w:type="dxa"/></w:tblPr><w:tblGrid><w:gridCol w:w="2500"/><w:gridCol w:w="2500"/></w:tblGrid><w:tr><w:tc><w:p><w:r><w:t>Table A</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>Table B</w:t></w:r></w:p></w:tc></w:tr></w:tbl>
                <w:p><w:r><w:br w:type="page"/></w:r></w:p><w:p><w:r><w:t>Second page</w:t></w:r></w:p>
                <w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr>
                </w:body></w:document>''')
        before = hashlib.sha256(source.read_bytes()).hexdigest()
        forward = convert(source, 'pdf', folder / 'converted')
        with pymupdf.open(forward) as pdf:
            assert len(pdf) == 2, 'Expected two pages'
            text = ''.join(page.get_text() for page in pdf)
            for token in ('First page', 'Second page', 'Table A', 'Table B', '한글'):
                assert token in text, 'Missing text: ' + token
            for i, page in enumerate(pdf):
                page.get_pixmap(matrix=pymupdf.Matrix(1, 1)).save(folder / f'forward-{i + 1}.png')
            scan = folder / 'scan.pdf'
            with pymupdf.open() as scanned:
                page = scanned.new_page(width=pdf[0].rect.width, height=pdf[0].rect.height)
                page.insert_image(page.rect, stream=pdf[0].get_pixmap().tobytes('png'))
                scanned.save(scan)
        assert hashlib.sha256(source.read_bytes()).hexdigest() == before, 'Source was modified'
        checks.append('docx->pdf: two pages, Korean, table text, source preserved')
        restored = convert(forward, 'docx', folder / 'converted')
        assert validate_docx(restored)['text'], 'Expected editable text'
        checks.append('pdf->docx: valid editable text')
        roundtrip = convert(restored, 'pdf', folder / 'converted')
        with pymupdf.open(roundtrip) as pdf:
            text = ''.join(page.get_text() for page in pdf)
            for token in ('First page', 'Second page', 'Table A', 'Table B', '한글'):
                assert token in text, 'Round-trip missing text: ' + token
            for i, page in enumerate(pdf):
                page.get_pixmap().save(folder / f'roundtrip-{i + 1}.png')
        checks.append('docx->pdf->docx->pdf: content retained')
        scan_docx = convert(scan, 'docx', folder / 'converted')
        assert any(validate_docx(scan_docx).values()), 'Scan output was empty'
        checks.append('scan pdf->docx: nonempty output, OCR not promised')
        report.update(ok=True, outputs=[str(p) for p in (forward, restored, roundtrip, scan_docx)])
    except Exception as exc:
        report['error'] = str(exc)
    (folder / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return 0 if report['ok'] else 1

def run(folder):
    folder = Path(folder).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    checks = []
    try:
        picture = folder / 'sample.png'
        Image.new('RGBA', (65, 49), (20, 120, 220, 120)).save(picture)
        for fmt in ['jpg', 'webp', 'gif', 'tiff', 'pdf']:
            result = convert(picture, fmt, folder / 'converted')
            assert result.exists()
            checks.append('png->' + fmt)
            if fmt == 'pdf':
                pages = convert(result, 'png', folder / 'converted')
                assert len(list(pages.iterdir())) == 1
                checks.append('pdf->png')
                slides = convert(result, 'pptx', folder / 'converted')
                from pptx import Presentation
                assert len(Presentation(slides).slides) == 1
                checks.append('pdf->pptx')
        movie = folder / 'sample.mp4'
        run_ffmpeg(['-f', 'lavfi', '-i', 'color=c=blue:size=64x48:rate=12:duration=0.5', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=0.5', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', str(movie)], threading.Event())
        assert 'mp3' in inspect(movie)['formats']
        for fmt in ['avi', 'webm', 'mp3', 'wav', 'gif']:
            result = convert(movie, fmt, folder / 'converted')
            assert result.exists()
            checks.append('mp4->' + fmt)
        report = {'ok': True, 'checks': checks}
    except Exception as exc:
        report = {'ok': False, 'checks': checks, 'error': str(exc)}
    (folder / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return 0 if report['ok'] else 1
