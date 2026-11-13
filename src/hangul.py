"""Local HWP conversions using the rhwp 0.9.0 command-line engine."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import time
import zipfile
from i18n import tr


def executable():
    root = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent.parent))
    return root / ('rhwp/rhwp.exe' if getattr(sys, 'frozen', False) else 'build/rhwp/rhwp.exe')


def convert_hangul(src, dst, cancel, progress):
    from engine import Cancelled, check, FLAGS
    exe = executable()
    if not exe.is_file():
        raise ValueError(tr('한글 변환 엔진이 없습니다. scripts/prepare_rhwp.ps1을 실행해 주세요.'))
    source, target = Path(src).suffix.lower(), Path(dst).suffix.lower()
    if source == '.pdf':
        args = ['import-pdf', str(src), str(dst)]
    elif target == '.pdf':
        args = ['export-pdf', str(src), '-o', str(dst)]
    elif target == '.hwpx':
        args = ['export-hwpx', str(src), str(dst)]
    else:
        args = ['convert', str(src), str(dst)]
    env = os.environ.copy()
    env['RHWP_WEBFONT_OFFLINE'] = '1'
    progress(tr('변환 중…'))
    check(cancel)
    with tempfile.TemporaryFile() as log:
        process = subprocess.Popen([str(exe), *args], stdout=log, stderr=log, env=env, creationflags=FLAGS)
        start = time.monotonic()
        try:
            while process.poll() is None:
                if cancel.wait(.1):
                    raise Cancelled()
                if time.monotonic() - start > 120:
                    raise ValueError(tr('변환 시간이 초과되었습니다.'))
            check(cancel)
            if process.returncode:
                log.seek(0)
                raise ValueError(tr('파일을 변환하지 못했습니다. 원본 파일이 정상적으로 열리는지 확인해 주세요.\n\n상세 오류: ') + log.read().decode('utf-8', errors='replace')[-1500:])
        finally:
            if process.poll() is None:
                process.kill()
            process.wait()
    if not Path(dst).is_file() or not Path(dst).stat().st_size:
        raise ValueError(tr('변환 결과가 생성되지 않았습니다.'))
    if target == '.pdf':
        import pymupdf
        with pymupdf.open(stream=Path(dst).read_bytes(), filetype='pdf') as pdf:
            if not len(pdf):
                raise ValueError(tr('PDF 결과에 페이지가 없습니다. 원본 파일을 확인해 주세요.'))
    elif target == '.hwp':
        with Path(dst).open('rb') as output:
            if output.read(8) != bytes.fromhex('d0cf11e0a1b11ae1'):
                raise ValueError(tr('변환 결과가 생성되지 않았습니다.'))
    elif not zipfile.is_zipfile(dst):
        raise ValueError(tr('변환 결과가 생성되지 않았습니다.'))
