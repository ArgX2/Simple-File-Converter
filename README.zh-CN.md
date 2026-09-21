# Simple File Converter

[한국어](README.md) | [English](README.en.md) | [日本語](README.ja.md) | **简体中文** | [Español](README.es.md)

适用于 Windows 的文件转换工具。当前版本为 `v1.0.0`。拖入或选择文件，指定输出格式，即可转换。也可以通过文件资源管理器的右键菜单转换单个文件。请查看[更新记录](CHANGELOG.md)。

## 下载

| 选项 | 下载 | 说明 |
| --- | --- | --- |
| **便携版 EXE** | [下载 Windows 版](https://github.com/ArgX2/Simple-File-Converter/releases) | 在发行版中选择 **Assets → Simple File Converter.exe**，无需安装。 |
| **源码 ZIP** | [下载源码](https://github.com/ArgX2/Simple-File-Converter/archive/refs/heads/main.zip) | main 分支的最新源码，运行需要 Python。 |
| **浏览源码** | [在 GitHub 查看](https://github.com/ArgX2/Simple-File-Converter/tree/main/src) | 无需下载即可阅读代码。 |

> EXE 附加到发行版后才能下载。如果发行版列表为空，表示尚未发布可执行文件。需要特定版本的源码时，请选择对应发行版中的 **Source code (zip)**。

下载并运行 EXE 后，将文件拖入窗口即可。需要 Office 软件的转换请参阅下方的运行要求。

## 主要功能

- 视频、音频、图片和 PDF 转换
- 批量转换与取消
- 保存到指定文件夹或各原文件所在的文件夹
- 保留原文件，输出名称重复时自动添加编号
- 资源管理器右键 → **Simple File Converter** → 输出格式
- 拖放高亮效果，以及区分提示、成功和错误的彩色通知
- 单个 EXE 的便携版
- 自动识别系统语言，可手动选择 16 种界面语言

### 语言设置

在左下角的 **语言** 菜单中选择 **自动（系统语言）** 或指定语言。设置立即生效，不会清空文件列表或结果，并应用于下次启动和右键转换窗口。转换过程中暂时不能切换语言。

支持韩语、英语、日语、简体中文、繁体中文、德语、法语、西班牙语、葡萄牙语、意大利语、俄语、越南语、泰语、印度尼西亚语、阿拉伯语和希伯来语。阿拉伯语和希伯来语使用从右到左的布局。不支持的系统语言将回退为英语。

翻译内置于 EXE，可离线使用。设置按当前 Windows 用户保存，移动 EXE 后仍然保留。Windows 原生文件选择窗口和外部程序的错误原文可能使用各自的语言。翻译尚未经过母语使用者审校，欢迎提出修改建议。

## 运行要求

- Windows 10/11，64 位
- 从源码运行或构建：Python 3.12，64 位
- PPT/PPTX → PDF、PDF → PPT：**需要安装 PowerPoint 或 LibreOffice**
- PDF → PPTX：无需安装 Office。每页保存为一张 **图片幻灯片**，不会恢复为文字、图形可单独编辑的对象。

## 支持的格式

| 输入 | 输出 |
| --- | --- |
| MP4, AVI, MKV, MOV, WEBM, WMV, M4V, MPG, MPEG | MP4, AVI, MKV, MOV, WEBM, GIF, PNG, JPG，以及音频提取 |
| MP3, WAV, FLAC, AAC, M4A, OGG, OPUS, WMA | MP3, WAV, FLAC, M4A, OGG, AAC, OPUS |
| PNG, JPG, JPEG, GIF, WEBP, BMP, TIF, TIFF, ICO | PNG, JPG, WEBP, BMP, TIFF, GIF, PDF |
| PDF | PNG, JPG, WEBP, TIFF, PPTX, PPT |
| PPT, PPTX | PDF |

实际能否转换取决于文件内容和已安装的软件。动态 GIF 转 MP4/WEBM 可在程序窗口中选择。

无法完整保留原始内容的转换会在程序中显示为 `不完整转换为 XXX`。

### 转换可用性

`O` 表示普通转换，`△` 表示内容、质量或结构可能变化的不完整转换，`X` 表示不支持。

| 输入 \\ 输出 | 图片 | 视频 | 音频 | PDF | PPTX | PPT |
| --- | --- | --- | --- | --- | --- | --- |
| PNG/JPG/GIF 等图片 | O/△ | △ | X | O | X | X |
| MP4/AVI 等视频 | △ | △ | △ | X | X | X |
| MP3/WAV 等音频 | X | X | △ | X | X | X |
| PDF | △ | X | X | X | △ | △ |
| PPT/PPTX | X | X | X | △ | X | X |

上方的支持格式表列出了可选择的具体输出格式；实际结果还取决于文件内容和已安装的 Office 软件。

## 使用方法

1. 将文件拖入窗口，或点击 **选择文件**。
2. 为每个文件选择输出格式。
3. 指定输出文件夹，或勾选 **保存到原文件夹**。
4. 点击 **开始转换**。

<img width="1450" height="1007" alt="程序窗口，截图为韩语界面" src="https://github.com/user-attachments/assets/5b0fcd4a-2e55-440a-aa7e-3615843dfaf8" />

双击失败项目可查看详情。通知会在 2.5 秒后自动关闭。在 PPT 相关确认中选择“是”后，直到列表完全清空前都不会再次询问。

### 资源管理器右键菜单

勾选程序底部的 **启用右键转换菜单**。Windows 11 中，该菜单位于 **显示更多选项** 内。选择格式后，结果保存在原文件所在的文件夹。

- 每次处理一个文件。
- 菜单根据扩展名显示选项，选择后再检查文件内容。例如，从没有音轨的视频提取音频可能失败。
- 将菜单注册到当前用户的注册表中。关闭此功能时，仅删除本程序的菜单项。
- 移动或删除 EXE 前，请先关闭菜单功能。移动后，在新位置关闭再开启此选项以重新注册。

<img width="814" height="273" alt="右键转换菜单，截图为韩语界面" src="https://github.com/user-attachments/assets/2f93bf9b-7e86-4e5b-b456-e4f97161345c" />

## 从源码运行

在仓库根目录中使用 PowerShell 执行以下命令，无需激活虚拟环境。

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe src\app.py
```

文件转换在本地完成。首次安装依赖需要网络连接；只有同意登录提示后，才会打开 Microsoft 登录页面。

## 测试

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

测试会在临时文件夹中生成测试文件。注册表测试使用内存中的替代实现，不会修改实际的资源管理器菜单。Office 的实际转换与右键菜单显示仍需单独手动验证。

## 构建单文件 EXE

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm "Simple File Converter.spec"
```

输出：`dist/Simple File Converter.exe`

```powershell
& ".\dist\Simple File Converter.exe" --self-test ".\build\smoke-check"
& ".\dist\Simple File Converter.exe" --smoke-test
```

`--self-test` 将结果写入指定文件夹的 `report.json`。详细构建与发布步骤请参阅[开发指南](docs/DEVELOPMENT.md)（韩语）。

## 限制

- PDF → 图片：以 144dpi 渲染所有页面，保存到单独的文件夹。
- 视频 → PNG/JPG、动态图片 → PNG/JPG/BMP：仅保存第一帧。
- 视频 → GIF：12fps，最大宽度 720px。
- 仅使用第一条视频和音频轨道，不复制字幕或其他轨道。
- Office 连接、激活或 Windows 会话问题不一定能通过浏览器登录解决。
- 便携版 EXE 运行时会将所需文件解压到临时文件夹，并在退出时清理。

## 项目结构

```text
src/                       程序源码与图标
tests/                     自动化测试
docs/                      使用、开发与发布指南
licenses/                  第三方组件许可声明
.github/                   Windows CI、Issue 和 PR 模板
Simple File Converter.spec 便携版构建配置
```

## 许可证状态

**本项目自身的源码尚未指定公开许可证。** 在所有者作出选择前，请勿认为 MIT 或其他许可证已适用。

第三方组件的条款独立适用。PyMuPDF/MuPDF 提供 [AGPL 或商业许可](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright)，FFmpeg 的[适用条款取决于构建配置](https://ffmpeg.org/legal.html)。公开分发前，请确认项目许可证，以及实际构建所需的源码提供要求。相关记录见 [THIRD_PARTY.txt](THIRD_PARTY.txt) 和[发布检查清单](docs/RELEASING.md)（韩语）。
