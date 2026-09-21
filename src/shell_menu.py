"""Per-user Explorer cascading menu; touches only this application's keys."""
from i18n import tr
import ctypes
import subprocess
import sys
import winreg
from pathlib import Path
from engine import IMAGES, MEDIA, PICTURES, VIDEO, AUDIO, imperfect_for_extension

CLASSES = r'Software\Classes'
STATE = r'Software\SimpleFileConverter'
MENU = 'SimpleFileConverter'
STORE = 'SimpleFileConverter.Menus'
AUDIO_INPUTS = {'mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg', 'opus', 'wma'}
EXTENSIONS = sorted(IMAGES | MEDIA | {'pdf', 'ppt', 'pptx'})

def launch_command():
    if getattr(sys, 'frozen', False): return [str(Path(sys.executable).resolve())]
    return [sys.executable, str(Path(__file__).with_name('app.py').resolve())]

def formats_for(extension):
    if extension in IMAGES: formats = PICTURES
    elif extension in AUDIO_INPUTS: formats = AUDIO
    elif extension in MEDIA: formats = VIDEO + ['gif', 'png', 'jpg'] + AUDIO
    elif extension == 'pdf': formats = ['png', 'jpg', 'webp', 'tiff', 'pptx', 'ppt']
    elif extension in {'ppt', 'pptx'}: formats = ['pdf']
    else: return []
    normalized = {'jpeg':'jpg', 'tif':'tiff'}.get(extension, extension)
    return [f for f in formats if f != normalized]

def menu_key(extension):
    return CLASSES + rf'\SystemFileAssociations\.{extension}\shell\{MENU}'

def put(path, values):
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_WRITE) as key:
        for name, value in values.items():
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)

def remove_tree(path):
    # Call sites pass only our menu, submenu store or state keys.
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            while winreg.QueryInfoKey(key)[0]:
                remove_tree(path + '\\' + winreg.EnumKey(key, 0))
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, path)
    except FileNotFoundError:
        pass

def refresh():
    ctypes.windll.shell32.SHChangeNotify(0x08000000, 0, None, None)

def is_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STATE) as key:
            return bool(winreg.QueryValueEx(key, 'Command')[0])
    except OSError:
        return False

def disable():
    for ext in EXTENSIONS: remove_tree(menu_key(ext))
    remove_tree(CLASSES + '\\' + STORE)
    remove_tree(STATE)
    refresh()

def enable():
    command = launch_command()
    disable()
    try:
        for ext in EXTENSIONS:
            group = STORE + '\\' + ext
            put(menu_key(ext), {'MUIVerb': 'Simple File Converter',
                'ExtendedSubCommandsKey': group,
                'Icon': '"' + command[0] + '",0'})
            for i, fmt in enumerate(formats_for(ext)):
                verb = CLASSES + '\\' + group + rf'\shell\{i:02d}_{fmt}'
                label = tr('{v0}로 불완전 변환', v0=fmt.upper()) if imperfect_for_extension(ext, fmt) else tr('{v0}로 변환', v0=fmt.upper())
                put(verb, {'MUIVerb': label})
                # Static verbs receive the single selected path as %1.
                cmd = subprocess.list2cmdline(command + ['--context-convert', fmt]) + ' "%1"'
                put(verb + '\\command', {'': cmd})
        put(STATE, {'Command': subprocess.list2cmdline(command)})
        refresh()
    except Exception:
        disable()
        raise
