# Simple File Converter

[한국어](README.md) | **English** | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | [Español](README.es.md)

A file converter for Windows. Current version: `v1.0.0`. Drop or select files, choose an output format, and convert. You can also convert a single file from the File Explorer context menu. See the [changelog](CHANGELOG.md).

## Download

| Option | Download | Details |
| --- | --- | --- |
| **Portable EXE** | [Download for Windows](https://github.com/ArgX2/Simple-File-Converter/releases) | Select **Assets → Simple File Converter.exe** in a release. No installation needed. |
| **Source ZIP** | [Download source](https://github.com/ArgX2/Simple-File-Converter/archive/refs/heads/main.zip) | Latest source from the main branch. Python is required to run it. |
| **Browse source** | [View on GitHub](https://github.com/ArgX2/Simple-File-Converter/tree/main/src) | Read the code without downloading it. |

> The EXE becomes available after it is attached to a release. If the release list is empty, no executable has been published yet. For a specific version's source, select **Source code (zip)** in that release.

Download and run the EXE, then drop your files into the window. See the requirements below for conversions that need Office software.

## Features

- Video, audio, image, and PDF conversion
- Batch conversion and cancellation
- Save to a selected folder or beside each original file
- Preserve originals and add a number when output names collide
- File Explorer: right-click → **Simple File Converter** → output format
- Drag feedback and colored information, success, and error notifications
- Single-file portable EXE
- Automatic system language detection and 16 selectable UI languages

### Language settings

Use **Language** at the bottom left to select **Automatic (system language)** or a specific language. Changes take effect immediately without clearing files or results. The setting is remembered for later launches and context-menu conversions. Language selection is disabled while converting.

Supported languages: Korean, English, Japanese, Simplified and Traditional Chinese, German, French, Spanish, Portuguese, Italian, Russian, Vietnamese, Thai, Indonesian, Arabic, and Hebrew. Arabic and Hebrew use a right-to-left layout. Unsupported system languages fall back to English.

Translations are bundled in the EXE and work offline. Preferences are saved for the current Windows user and remain available if you move the EXE. Native Windows file dialogs and external error messages may use their own language. Translations have not been reviewed by native speakers; corrections are welcome.

## Requirements

- Windows 10/11, 64-bit
- Running or building from source: Python 3.12, 64-bit
- PPT/PPTX → PDF and PDF → PPT: **PowerPoint or LibreOffice must be installed**
- PDF → PPTX: no Office installation needed. Each page becomes an **image slide**; text and shapes are not restored as individually editable objects.

## Supported formats

| Input | Output |
| --- | --- |
| MP4, AVI, MKV, MOV, WEBM, WMV, M4V, MPG, MPEG | MP4, AVI, MKV, MOV, WEBM, GIF, PNG, JPG, and audio extraction |
| MP3, WAV, FLAC, AAC, M4A, OGG, OPUS, WMA | MP3, WAV, FLAC, M4A, OGG, AAC, OPUS |
| PNG, JPG, JPEG, GIF, WEBP, BMP, TIF, TIFF, ICO | PNG, JPG, WEBP, BMP, TIFF, GIF, PDF |
| PDF | PNG, JPG, WEBP, TIFF, PPTX, PPT |
| PPT, PPTX | PDF |

Conversion availability depends on the file contents and installed software. Animated GIF → MP4/WEBM is available in the application window.

Formats that may not preserve the original perfectly are labeled `Convert to XXX with possible loss` in the application.

### Conversion status

`O` means a standard conversion, `△` means an incomplete conversion where content, quality, or structure may change, and `X` means unsupported.

| Input \\ Output | Images | Video | Audio | PDF | PPTX | PPT |
| --- | --- | --- | --- | --- | --- | --- |
| PNG/JPG/GIF and other images | O/△ | △ | X | O | X | X |
| MP4/AVI and other video | △ | △ | △ | X | X | X |
| MP3/WAV and other audio | X | X | △ | X | X | X |
| PDF | △ | X | X | X | △ | △ |
| PPT/PPTX | X | X | X | △ | X | X |

The detailed selectable outputs are listed in the supported formats table above and may vary with file contents and installed Office software.

## Usage

1. Drop files into the window or click **Choose files**.
2. Select an output format for each file.
3. Choose an output folder or enable **Save beside originals**.
4. Click **Convert**.

<img width="1450" height="1007" alt="Application window, shown in Korean" src="https://github.com/user-attachments/assets/5b0fcd4a-2e55-440a-aa7e-3615843dfaf8" />

Double-click a failed item for details. Notifications close automatically after 2.5 seconds. Choosing Yes in the presentation confirmation skips further confirmations until the file list is completely empty.

### File Explorer context menu

Enable **Enable Explorer conversion menu** at the bottom of the application. On Windows 11, it appears under **Show more options**. Choose a format to save the result beside the original file.

- Works with one file at a time.
- Menu options are based on the extension; file contents are checked after selection. For example, extracting audio from a silent video can fail.
- Registers the menu for the current Windows user. Disabling it removes only this application's entries.
- Disable the menu before moving or deleting the EXE. After moving it, turn the option off and on again from the new location.

<img width="814" height="273" alt="File Explorer conversion menu, shown in Korean" src="https://github.com/user-attachments/assets/2f93bf9b-7e86-4e5b-b456-e4f97161345c" />

## Run from source

Run these commands in PowerShell from the repository root. Activating the virtual environment is not required.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe src\app.py
```

Files are converted locally. Initial dependency installation requires internet access. The Microsoft sign-in page opens only if you accept the sign-in prompt.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Tests generate fixtures in temporary folders. Registry tests use an in-memory substitute and do not change the real Explorer menu. Actual Office conversion and Explorer integration require separate manual checks.

## Build a portable EXE

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm "Simple File Converter.spec"
```

Output: `dist/Simple File Converter.exe`

```powershell
& ".\dist\Simple File Converter.exe" --self-test ".\build\smoke-check"
& ".\dist\Simple File Converter.exe" --smoke-test
```

`--self-test` writes `report.json` in the specified folder. See the [development guide](docs/DEVELOPMENT.md) for build and release details (in Korean).

## Limitations

- PDF → images: renders all pages at 144 dpi into a separate folder.
- Video → PNG/JPG and animated image → PNG/JPG/BMP: exports only the first frame.
- Video → GIF: 12 fps, maximum width 720 px.
- Uses the first video/audio tracks; subtitles and additional tracks are not copied.
- Browser sign-in alone may not resolve Office connection, activation, or Windows session errors.
- The portable EXE extracts runtime files to a temporary folder and cleans them up on exit.

## Project structure

```text
src/                       Application source and icon
tests/                     Automated tests
docs/                      Usage, development, and release guides
licenses/                  Third-party license notices
.github/                   Windows CI and issue/PR templates
Simple File Converter.spec Portable build configuration
```

## License status

**No public license has been assigned to this project's own source code yet.** Do not assume an MIT or other license applies until the owner chooses one.

Third-party terms apply separately. PyMuPDF/MuPDF offers [AGPL or commercial licensing](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright), and FFmpeg's [terms depend on its build configuration](https://ffmpeg.org/legal.html). Before public distribution, review the project license and source-distribution requirements for the actual build. See [THIRD_PARTY.txt](THIRD_PARTY.txt) and the [release checklist](docs/RELEASING.md) (in Korean).
