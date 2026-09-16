# Simple File Converter

[한국어](README.md) | [English](README.en.md) | **日本語** | [简体中文](README.zh-CN.md) | [Español](README.es.md)

Windows用のファイル変換ソフトです。ファイルをドラッグするか選択し、出力形式を指定して変換できます。エクスプローラーの右クリックメニューからも変換できます。

## ダウンロード

| 種類 | ダウンロード | 説明 |
| --- | --- | --- |
| **ポータブルEXE** | [Windows版をダウンロード](https://github.com/ArgX2/Simple-File-Converter/releases) | リリースの **Assets → Simple File Converter.exe** を選択。インストール不要です。 |
| **ソースコードZIP** | [ソースをダウンロード](https://github.com/ArgX2/Simple-File-Converter/archive/refs/heads/main.zip) | mainブランチの最新ソースです。実行にはPythonが必要です。 |
| **ソースを閲覧** | [GitHubで見る](https://github.com/ArgX2/Simple-File-Converter/tree/main/src) | ダウンロードせずにコードを確認できます。 |

> EXEはリリースに添付された後にダウンロードできます。リリース一覧が空の場合、実行ファイルはまだ公開されていません。特定バージョンのソースは、そのリリースの **Source code (zip)** を選択してください。

EXEをダウンロードして起動し、ファイルをドラッグしてください。Officeソフトが必要な変換については、以下の動作環境をご確認ください。

## 主な機能

- 動画・音声・画像・PDFの変換
- 複数ファイルの一括変換とキャンセル
- 指定フォルダー、または各ファイルの元のフォルダーに保存
- 元のファイルを保持し、出力名が重複する場合は番号を追加
- エクスプローラーで右クリック → **Simple File Converter** → 出力形式
- ドラッグの強調表示と、案内・成功・エラーを色分けした通知
- 単一EXEのポータブル版
- システム言語の自動検出と16言語の選択

### 言語設定

左下の **言語** から **自動（システム言語）** または使用する言語を選択してください。ファイル一覧や結果を保持したまますぐに反映され、次回起動時と右クリック変換にも適用されます。変換中は言語を変更できません。

韓国語、英語、日本語、中国語（簡体字・繁体字）、ドイツ語、フランス語、スペイン語、ポルトガル語、イタリア語、ロシア語、ベトナム語、タイ語、インドネシア語、アラビア語、ヘブライ語に対応しています。アラビア語とヘブライ語は右から左への画面配置になります。未対応のシステム言語では英語を表示します。

翻訳はEXEに含まれ、オフラインで動作します。設定は現在のWindowsユーザーに保存され、EXEを移動しても維持されます。Windows標準のファイル選択画面や外部プログラムのエラー原文は、そのプログラムの言語で表示される場合があります。翻訳はネイティブ話者による校閲前です。改善提案を歓迎します。

## 動作環境

- Windows 10/11、64ビット
- ソースからの実行・ビルド：Python 3.12、64ビット
- PPT/PPTX → PDF、PDF → PPT：**PowerPointまたはLibreOfficeのインストールが必要**
- PDF → PPTX：Office不要。各ページを **画像スライド** として保存するため、文字や図形を個別に編集できる状態には復元しません。

## 対応形式

| 入力 | 出力 |
| --- | --- |
| MP4, AVI, MKV, MOV, WEBM, WMV, M4V, MPG, MPEG | MP4, AVI, MKV, MOV, WEBM, GIF, PNG, JPG、および音声抽出 |
| MP3, WAV, FLAC, AAC, M4A, OGG, OPUS, WMA | MP3, WAV, FLAC, M4A, OGG, AAC, OPUS |
| PNG, JPG, JPEG, GIF, WEBP, BMP, TIF, TIFF, ICO | PNG, JPG, WEBP, BMP, TIFF, GIF, PDF |
| PDF | PNG, JPG, WEBP, TIFF, PPTX, PPT |
| PPT, PPTX | PDF |

実際に変換できるかどうかは、ファイルの内容やインストール済みソフトに依存します。アニメーションGIFからMP4/WEBMへの変換は、アプリ画面で選択できます。

## 使い方

1. ファイルをドラッグするか、**ファイルを選択** を押します。
2. ファイルごとに出力形式を選択します。
3. 保存先を指定するか、**元のフォルダーに保存** をオンにします。
4. **変換開始** を押します。

<img width="1450" height="1007" alt="アプリ画面（韓国語表示）" src="https://github.com/user-attachments/assets/5b0fcd4a-2e55-440a-aa7e-3615843dfaf8" />

失敗した項目をダブルクリックすると詳細を確認できます。通知は2.5秒後に自動で閉じます。PPT関連の確認で「はい」を選ぶと、一覧を完全に空にするまで再確認を省略します。

### エクスプローラーの右クリックメニュー

画面下部の **右クリック変換メニューを有効にする** をオンにしてください。Windows 11では **その他のオプションを表示** 内に表示されます。形式を選択すると元のファイルと同じフォルダーに保存します。

- 一度に1ファイルを処理します。
- メニューは拡張子に基づき、選択後に内容を検査します。音声のない動画からの音声抽出などは失敗する場合があります。
- 現在のユーザーのレジストリに登録します。無効にすると、このアプリの項目だけを削除します。
- EXEの移動・削除前にメニューを無効にしてください。移動後は新しい場所で設定をオフにしてからオンにし、再登録してください。

<img width="814" height="273" alt="右クリック変換メニュー（韓国語表示）" src="https://github.com/user-attachments/assets/2f93bf9b-7e86-4e5b-b456-e4f97161345c" />

## ソースから実行

リポジトリのルートでPowerShellから実行します。仮想環境の有効化は不要です。

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe src\app.py
```

変換はローカルで処理します。初回の依存パッケージのインストールにはインターネットが必要です。ログイン案内に同意した場合はMicrosoftのログインページを開きます。

## テスト

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

テスト用ファイルは一時フォルダーに生成します。レジストリのテストはメモリ上の代替データを使うため、実際の右クリックメニューを変更しません。Officeの実変換とエクスプローラーでの表示は別途手動確認が必要です。

## 単一EXEのビルド

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm "Simple File Converter.spec"
```

出力：`dist/Simple File Converter.exe`

```powershell
& ".\dist\Simple File Converter.exe" --self-test ".\build\smoke-check"
& ".\dist\Simple File Converter.exe" --smoke-test
```

`--self-test`の結果は指定フォルダーの`report.json`に保存します。詳細は[開発ガイド](docs/DEVELOPMENT.md)（韓国語）をご覧ください。

## 制限事項

- PDF → 画像：全ページを144dpiで描画し、専用フォルダーに保存します。
- 動画 → PNG/JPG、アニメーション画像 → PNG/JPG/BMP：最初のフレームのみ保存します。
- 動画 → GIF：12fps、最大幅720pxです。
- 最初の映像・音声トラックを使用し、字幕や追加トラックはコピーしません。
- Officeの接続・認証・Windowsセッションの問題は、ブラウザーでのログインだけでは解決しない場合があります。
- ポータブルEXEは実行時に必要なファイルを一時フォルダーに展開し、終了時に削除します。

## 構成

```text
src/                       ソースとアイコン
tests/                     自動テスト
docs/                      使用・開発・配布ガイド
licenses/                  外部コンポーネントのライセンス表記
.github/                   Windows CI、Issue・PRテンプレート
Simple File Converter.spec ポータブル版のビルド設定
```

## ライセンスの状態

**本プロジェクト独自のソースコードには、公開ライセンスをまだ指定していません。** 所有者が選択するまでは、MITなどのライセンスが適用されると解釈しないでください。

外部コンポーネントには別途条件が適用されます。PyMuPDF/MuPDFは[AGPLまたは商用ライセンス](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright)を提供し、FFmpegは[ビルド設定によって条件が異なります](https://ffmpeg.org/legal.html)。公開配布前にプロジェクトのライセンスと実際のビルドに必要なソース提供条件をご確認ください。[THIRD_PARTY.txt](THIRD_PARTY.txt)と[配布チェックリスト](docs/RELEASING.md)（韓国語）に関連情報があります。
