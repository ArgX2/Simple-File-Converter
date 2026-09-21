from i18n import tr
from pathlib import Path
import os
import re
import subprocess
import tempfile
import threading
import shutil
from PIL import Image, ImageOps
import pymupdf
import imageio_ffmpeg

IMAGES = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'tif', 'tiff', 'ico'}
MEDIA = {'mp4', 'avi', 'mkv', 'mov', 'webm', 'wmv', 'm4v', 'mpg', 'mpeg', 'mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg', 'opus', 'wma'}
AUDIO = ['mp3', 'wav', 'flac', 'm4a', 'ogg', 'aac', 'opus']
VIDEO = ['mp4', 'avi', 'mkv', 'mov', 'webm']
PICTURES = ['png', 'jpg', 'webp', 'bmp', 'tiff', 'gif', 'pdf']
FLAGS = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

class Cancelled(Exception):
    pass

def inspect(path):
    path = Path(path)
    ext = path.suffix.lower()[1:]
    if ext in {'ppt', 'pptx'}:
        if not path.is_file() or path.stat().st_size == 0: raise ValueError(tr('파일이 비어 있거나 찾을 수 없습니다. 원본을 확인해 주세요.'))
        return {'kind': 'presentation', 'formats': ['pdf'], 'detail': ext.upper()}
    if ext == 'pdf':
        with pymupdf.open(path) as doc:
            if doc.needs_pass:
                raise ValueError(tr('암호가 걸린 PDF입니다. 암호를 해제한 파일을 선택해 주세요.'))
            if not len(doc):
                raise ValueError(tr('페이지가 없는 PDF입니다.'))
            return {'kind': 'pdf', 'formats': ['png', 'jpg', 'webp', 'tiff', 'txt', 'pptx', 'ppt'], 'detail': tr('PDF · {v0}페이지', v0=len(doc))}
    if ext in IMAGES:
        with Image.open(path) as im:
            im.load()
            frames = getattr(im, 'n_frames', 1)
            formats = PICTURES + (['mp4', 'webm'] if frames > 1 and ext == 'gif' else [])
            return {'kind': 'image', 'formats': formats, 'detail': tr('{v0} × {v1} · {v2}프레임', v0=im.width, v1=im.height, v2=frames)}
    if ext in MEDIA:
        result = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-i', str(path)], capture_output=True, creationflags=FLAGS, timeout=20)
        info = result.stderr.decode('utf-8', errors='replace')
        video = bool(re.search(r'Stream .*Video:', info))
        audio = bool(re.search(r'Stream .*Audio:', info))
        if not video and not audio:
            raise ValueError(tr('읽을 수 없는 영상 또는 음성 파일입니다.'))
        return {'kind': 'media', 'formats': (VIDEO + ['gif', 'png', 'jpg'] if video else []) + (AUDIO if audio else []), 'detail': tr('영상 + 음성' if audio else '영상 · 음성 없음') if video else tr('음성')}
    raise ValueError(tr('지원하지 않는 파일 형식입니다.'))

def check(cancel):
    if cancel.is_set():
        raise Cancelled()

def rgb(im):
    rgba = im.convert('RGBA')
    bg = Image.new('RGB', im.size, 'white')
    bg.paste(rgba, mask=rgba.getchannel('A'))
    return bg

def run_ffmpeg(args, cancel):
    with tempfile.TemporaryFile() as log:
        proc = subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-loglevel', 'error', '-nostdin', '-y', *args], stdout=subprocess.DEVNULL, stderr=log, creationflags=FLAGS)
        try:
            while proc.poll() is None:
                if cancel.wait(0.15):
                    raise Cancelled()
            if proc.returncode:
                log.seek(0)
                raise ValueError(tr('파일을 변환하지 못했습니다. 원본 파일이 정상적으로 열리는지 확인해 주세요.\n\n상세 오류: ') + log.read().decode('utf-8', errors='replace')[-1500:])
        finally:
            if proc.poll() is None:
                proc.kill()
            proc.wait()

def media_convert(src, dst, fmt, cancel):
    args = ['-i', str(src)]
    even = 'pad=ceil(iw/2)*2:ceil(ih/2)*2'
    if fmt in AUDIO:
        args += ['-map', '0:a:0', '-vn']
        args += {'mp3': ['-c:a', 'libmp3lame', '-q:a', '2'], 'wav': ['-c:a', 'pcm_s16le'], 'flac': ['-c:a', 'flac'], 'm4a': ['-c:a', 'aac', '-b:a', '192k'], 'aac': ['-c:a', 'aac', '-b:a', '192k'], 'ogg': ['-c:a', 'libvorbis', '-q:a', '5'], 'opus': ['-c:a', 'libopus', '-b:a', '128k']}[fmt]
    elif fmt in VIDEO:
        args += ['-map', '0:v:0', '-map', '0:a:0?', '-vf', even, '-pix_fmt', 'yuv420p']
        if fmt == 'webm':
            args += ['-c:v', 'libvpx-vp9', '-crf', '32', '-b:v', '0', '-c:a', 'libopus']
        elif fmt == 'avi':
            args += ['-c:v', 'mpeg4', '-q:v', '3', '-c:a', 'libmp3lame']
        else:
            args += ['-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-c:a', 'aac', '-b:a', '192k']
            if fmt in ['mp4', 'mov']:
                args += ['-movflags', '+faststart']
    elif fmt == 'gif':
        args += ['-filter_complex', '[0:v:0]fps=12,scale=min(720\\,iw):-1:flags=lanczos,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse', '-an', '-loop', '0']
    else:
        args += ['-map', '0:v:0', '-frames:v', '1', '-update', '1']
    run_ffmpeg(args + [str(dst)], cancel)

def convert(src, fmt, folder, meta=None, cancel=None, progress=lambda text: None):
    src, folder = Path(src), Path(folder)
    cancel = cancel or threading.Event()
    meta = meta or inspect(src)
    if fmt not in meta['formats']:
        raise ValueError(tr('이 파일에서 지원하지 않는 변환입니다.'))
    folder.mkdir(parents=True, exist_ok=True)
    check(cancel)
    with tempfile.TemporaryDirectory(prefix='.converter-', dir=folder) as temp:
        stage = Path(temp)
        dst = stage / (src.stem + '.' + fmt)
        if meta['kind'] == 'presentation':
            from office import office_convert
            office_convert(src, dst, cancel)
            with pymupdf.open(dst) as doc:
                if not len(doc): raise ValueError(tr('PDF 결과에 페이지가 없습니다. 원본 파일을 확인해 주세요.'))
        elif meta['kind'] == 'pdf' and fmt in {'ppt', 'pptx'}:
            from office import pdf_to_slides
            pdf_to_slides(src, dst, cancel, progress)
        elif meta['kind'] == 'media' or fmt in VIDEO:
            media_convert(src, dst, fmt, cancel)
        elif meta['kind'] == 'pdf' and fmt == 'txt':
            with pymupdf.open(src) as doc, dst.open('w', encoding='utf-8', newline='') as text_file:
                for i, page in enumerate(doc):
                    check(cancel)
                    progress(tr('PDF {v0}/{v1}페이지', v0=i + 1, v1=len(doc)))
                    text = page.get_text('text')
                    if i:
                        text_file.write('\n\n')
                    text_file.write(text.rstrip())
                    text_file.write('\n')
        elif meta['kind'] == 'pdf':
            dst = stage / (src.stem + '_' + fmt + '_pages')
            dst.mkdir()
            with pymupdf.open(src) as doc:
                for i, page in enumerate(doc):
                    check(cancel)
                    progress(tr('PDF {v0}/{v1}페이지', v0=i + 1, v1=len(doc)))
                    pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
                    with Image.frombytes('RGB', [pix.width, pix.height], pix.samples) as im:
                        im.save(dst / f'page_{i + 1:04d}.{fmt}', quality=95)
        else:
            with Image.open(src) as im:
                count = getattr(im, 'n_frames', 1)
                if count > 1 and fmt in {'gif', 'webp', 'tiff', 'pdf'}:
                    frames, durations = [], []
                    try:
                        for i in range(count):
                            check(cancel)
                            im.seek(i)
                            frame = ImageOps.exif_transpose(im).copy()
                            frames.append(rgb(frame) if fmt == 'pdf' else frame.convert('RGBA'))
                            durations.append(im.info.get('duration', 100))
                        kwargs = {'save_all': True, 'append_images': frames[1:]}
                        if fmt in {'gif', 'webp'}:
                            kwargs.update(duration=durations, loop=im.info.get('loop', 0))
                        frames[0].save(dst, **kwargs)
                    finally:
                        for frame in frames:
                            frame.close()
                else:
                    frame = ImageOps.exif_transpose(im)
                    if fmt in {'jpg', 'pdf', 'bmp'}:
                        frame = rgb(frame)
                    frame.save(dst, quality=95)
        check(cancel)
        if not dst.exists() or (dst.is_file() and dst.stat().st_size == 0):
            raise ValueError(tr('변환 결과가 생성되지 않았습니다.'))
        # Windows rename is atomic and refuses to replace an existing destination.
        target = folder / dst.name
        n = 1
        while True:
            try:
                dst.rename(target)
                return target
            except FileExistsError:
                target = folder / (f'{dst.stem} ({n}){dst.suffix}' if dst.is_file() else f'{dst.name} ({n})')
                n += 1
