"""Optional packaged-runtime smoke check: Simple File Converter.exe --self-test <report-folder>."""
import json
import threading
from pathlib import Path
from PIL import Image
from engine import convert, inspect, run_ffmpeg

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
