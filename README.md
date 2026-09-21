# Simple File Converter

**한국어** | [English](README.en.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | [Español](README.es.md)

Windows용 파일 변환 프로그램입니다. 현재 버전은 `v1.0.0`입니다. 파일을 드래그하거나 선택하고, 원하는 형식으로 변환하세요. 탐색기 우클릭 메뉴에서도 단일 파일을 바로 변환할 수 있습니다.

## 다운로드

| 원하는 항목 | 다운로드 | 안내 |
| --- | --- | --- |
| **포터블 EXE** | [Windows 실행 파일 받기](https://github.com/ArgX2/Simple-File-Converter/releases) | 릴리스의 **Assets → Simple File Converter.exe** 선택. 설치 없이 실행하세요. |
| **소스코드 ZIP** | [소스코드 다운로드](https://github.com/ArgX2/Simple-File-Converter/archive/refs/heads/main.zip) | main 브랜치의 최신 소스입니다. 직접 실행하려면 Python이 필요합니다. |
| **소스코드 살펴보기** | [GitHub에서 보기](https://github.com/ArgX2/Simple-File-Converter/tree/main/src) | 다운로드 없이 코드를 확인하세요. |

> EXE는 릴리스에 첨부된 뒤 다운로드할 수 있습니다. 릴리스가 비어 있다면 아직 실행 파일이 배포되지 않은 상태입니다. 특정 버전의 소스는 해당 릴리스의 **Source code (zip)**을 선택하세요.

EXE를 다운로드한 뒤 실행하고 파일을 드래그하면 됩니다. 지원 환경과 Office 설치가 필요한 변환은 아래를 참고하세요.

## 주요 기능

- 영상·음성·이미지·PDF 변환
- 여러 파일의 일괄 변환과 취소
- 지정 폴더 또는 각 원본 폴더에 결과 저장
- 원본 보존 및 이름 충돌 시 자동 번호 추가
- 탐색기 우클릭 → **Simple File Converter** → 변환 형식 선택
- 드래그 강조 효과와 색상별 알림: 안내·성공·오류
- 단일 EXE 포터블 빌드
- 시스템 언어 자동 감지 및 프로그램 내 16개 언어 선택

### 언어 설정

좌측 하단의 **언어** 메뉴에서 **자동 (시스템 언어)** 또는 원하는 언어를 선택하세요. 파일 목록과 결과를 유지한 채 바로 적용되며, 다음 실행과 우클릭 변환 창에도 같은 설정을 사용합니다. 변환 중에는 언어 선택이 잠시 비활성화됩니다.

한국어, 영어, 일본어, 중국어 간체·번체, 독일어, 프랑스어, 스페인어, 포르투갈어, 이탈리아어, 러시아어, 베트남어, 태국어, 인도네시아어, 아랍어, 히브리어를 지원합니다. 아랍어·히브리어에서는 화면 배치가 오른쪽에서 왼쪽으로 바뀝니다. 지원하지 않는 시스템 언어는 영어로 표시합니다.

번역은 EXE에 포함되어 인터넷 연결 없이 작동합니다. 설정은 현재 Windows 사용자에게 저장되며 EXE를 옮겨도 유지됩니다. Windows 기본 파일 선택창과 외부 프로그램의 오류 원문은 해당 프로그램의 언어로 표시될 수 있습니다. 번역 문구는 원어민 검수를 거치지 않았으며 개선 제안을 환영합니다.

## 지원 환경

- Windows 10/11, 64비트
- 소스 실행·빌드: Python 3.12, 64비트
- PPT/PPTX → PDF 및 PDF → PPT: **PowerPoint 또는 LibreOffice 설치 필요**
- PDF → PPTX: Office 설치 불필요. 각 페이지를 **이미지 슬라이드**로 저장합니다.

## 변환 형식

| 입력 | 출력 |
| --- | --- |
| MP4, AVI, MKV, MOV, WEBM, WMV, M4V, MPG, MPEG | MP4, AVI, MKV, MOV, WEBM, GIF, PNG, JPG 및 음성 추출 |
| MP3, WAV, FLAC, AAC, M4A, OGG, OPUS, WMA | MP3, WAV, FLAC, M4A, OGG, AAC, OPUS |
| PNG, JPG, JPEG, GIF, WEBP, BMP, TIF, TIFF, ICO | PNG, JPG, WEBP, BMP, TIFF, GIF, PDF |
| PDF | PNG, JPG, WEBP, TIFF, PPTX, PPT |
| PPT, PPTX | PDF |

실제 변환 가능 여부는 파일 내용과 설치된 프로그램에 따라 달라집니다. 움직이는 GIF의 MP4/WEBM 변환은 프로그램 창에서 선택할 수 있습니다.

완전한 보존이 어려운 항목은 프로그램에서 `XXX로 불완전 변환` 형식으로 표시합니다. 실제 변환 실패와 구분되는 품질 안내입니다.

## 사용 방법

1. 프로그램에 파일을 드래그하거나 **파일 선택**을 누릅니다.
2. 파일별 변환 형식을 선택합니다.
3. 저장 폴더를 지정하거나 **원본 폴더에 저장**을 체크합니다.
4. **변환 시작**을 누릅니다.
<img width="1450" height="1007" alt="스크린샷 2026-09-16 184333" src="https://github.com/user-attachments/assets/5b0fcd4a-2e55-440a-aa7e-3615843dfaf8" />


변환 실패 항목은 두 번 클릭하면 상세 내용을 볼 수 있습니다. 알림은 2.5초 후 자동으로 닫힙니다. PPT 관련 확인에서 예를 선택하면 목록을 완전히 비울 때까지 재확인을 생략합니다.

### 탐색기 우클릭 메뉴

프로그램 하단의 **우클릭 변환 메뉴 사용**을 체크하세요. Windows 11에서는 **더 많은 옵션 표시** 안에 나타납니다. 형식을 선택하면 결과를 원본 파일과 같은 폴더에 저장합니다.

- 한 번에 한 파일을 대상으로 합니다.
- 메뉴는 확장자 기준이며, 선택 후 파일 내용을 검사합니다. 음성이 없는 영상에서 음성을 추출하는 등의 작업은 실패할 수 있습니다.
- 현재 사용자 계정의 레지스트리에 메뉴를 등록합니다. 해제하면 이 프로그램의 메뉴만 제거합니다.
- EXE를 옮기거나 삭제하기 전 메뉴를 해제하세요. 위치를 바꿨다면 새 위치에서 체크를 껐다 켜 다시 등록하세요.

<img width="814" height="273" alt="스크린샷 2026-09-16 183301" src="https://github.com/user-attachments/assets/2f93bf9b-7e86-4e5b-b456-e4f97161345c" />



## 소스에서 실행

저장소 루트에서 PowerShell로 실행합니다. 가상환경 활성화는 필요하지 않습니다.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe src\app.py
```

파일 변환은 로컬에서 처리합니다. 최초 의존성 설치에는 인터넷이 필요하며, 로그인 안내에서 동의한 경우 Microsoft 로그인 페이지가 열립니다.

## 테스트

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

테스트는 임시 폴더에 자체 파일을 생성합니다. 레지스트리 등록 테스트는 메모리 기반 대체 저장소를 사용하므로 실제 탐색기 메뉴를 변경하지 않습니다. Office 실변환과 탐색기 메뉴 표시는 별도 수동 검증 대상입니다.

## 단일 EXE 빌드

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm "Simple File Converter.spec"
```

결과: `dist/Simple File Converter.exe`

```powershell
& ".\dist\Simple File Converter.exe" --self-test ".\build\smoke-check"
& ".\dist\Simple File Converter.exe" --smoke-test
```

`--self-test` 결과는 지정 폴더의 `report.json`에 기록됩니다. 상세 빌드·배포 절차는 [개발 안내](docs/DEVELOPMENT.md)를 참고하세요.

## 제한 사항

- PDF → 이미지: 전체 페이지를 144dpi로 렌더링하여 별도 폴더에 저장합니다.
- 영상 → PNG/JPG, 움직이는 이미지 → PNG/JPG/BMP: 첫 프레임만 저장합니다.
- 영상 → GIF: 12fps, 최대 너비 720px입니다.
- 영상의 첫 영상/음성 트랙을 사용하며 자막과 추가 트랙은 복사하지 않습니다.
- Office 연결·인증·Windows 세션 문제는 브라우저 로그인만으로 해결되지 않을 수 있습니다.
- 포터블 EXE는 실행 중 필요한 파일을 임시 폴더에 풀고 종료 시 정리합니다.

## 프로젝트 구조

```text
src/                    프로그램 소스와 아이콘
tests/                  자동 테스트
docs/                   사용·개발·배포 안내
licenses/               외부 구성요소 라이선스 고지
.github/                Windows CI와 이슈/PR 양식
Simple File Converter.spec  포터블 빌드 설정
```

## 예정 기능

Word(`DOC`, `DOCX`)와 한글(`HWP`, `HWPX`)의 PDF 변환을 우선 검토하고 있습니다. PDF ↔ HTML·PNG·Markdown, 이미지 묶음 ↔ 다중 페이지 PDF 등 양방향 후보와 구현 조건은 [개선 로드맵](docs/ROADMAP.md)에 기록해 두었습니다.

원본의 편집 구조나 배치를 완전히 보장하기 어려운 변환에는 **`XXX로 불완전 변환`**처럼 표시합니다. 이 표기는 현재 16개 UI 언어로 함께 제공됩니다.

## 라이선스 상태

**프로젝트 자체의 공개 라이선스는 아직 지정하지 않았습니다.** 저장소 소유자가 선택하기 전까지 MIT 등의 라이선스가 적용된 것으로 간주하지 마세요.

외부 구성요소의 조건은 별개입니다. PyMuPDF/MuPDF는 [AGPL 또는 상용 라이선스](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright)를 제공하며, FFmpeg는 [빌드 옵션에 따라 적용 조건이 달라집니다](https://ffmpeg.org/legal.html). 공개 배포 전 프로젝트 라이선스 및 해당 빌드의 소스 제공 요건을 확인하세요. [THIRD_PARTY.txt](THIRD_PARTY.txt)와 [배포 점검](docs/RELEASING.md)에 관련 기록을 모았습니다.
