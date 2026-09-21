# 개발 안내

Python 3.12와 Windows x64를 기준으로 합니다. 프로젝트 작업 기준은 루트의 `AGENTS.md`를 따릅니다.

## 코드 역할

| 파일 | 역할 |
| --- | --- |
| `src/app.py` | 메인 UI, 작업 스레드, 저장 위치, PPT 확인 상태 |
| `src/engine.py` | 파일 검사와 변환, 취소, 원본 보존 |
| `src/effects.py` | 드래그 강조, 버튼 효과, 알림 |
| `src/office.py`, `src/office.ps1` | Office 연동 및 PDF 이미지 슬라이드 생성 |
| `src/document.py`, `src/word.ps1` | DOCX 검사, PDF↔DOCX 변환 및 품질 안내 |
| `src/shell_menu.py` | 현재 사용자 우클릭 메뉴 등록·해제 |
| `src/quick_convert.py` | 우클릭 변환 진행·결과 창 |
| `src/diagnostics.py` | 배포 실행 파일의 변환 진단 |

## 빌드

루트에서 `python -m PyInstaller --noconfirm "Simple File Converter.spec"`를 실행합니다.
`build/`는 중간 결과, `dist/`는 최종 결과입니다. 두 폴더 모두 Git 추적에서 제외됩니다.

소스와 라이선스 고지는 실행 파일에 함께 포함됩니다. 일부 Python 배포판의 ICU DLL이 Qt의 Windows 시스템 ICU와 충돌할 수 있어, 기존 동작대로 해당 DLL은 번들에서 제외합니다.

## 내부 명령

```powershell
python src\app.py --context-convert jpg "C:\Example\image.png"
python src\app.py --self-test "build\diagnostics"
python src\app.py --document-self-test "build\document-diagnostics"
python src\app.py --smoke-test
```

`--context-convert`는 단일 파일을 받아 UI 알림을 표시하며 원본 폴더에 저장합니다. 완료 알림과 오류 알림이 닫힌 뒤 종료합니다.

## 검증 범위

자동 테스트는 원본 보존, 파일명 충돌, PDF 페이지/슬라이드 수, 취소, 저장 경로, 확인 팝업 상태를 점검합니다. 외부 Office 프로그램을 실행하거나 실제 레지스트리를 변경하지 않습니다.

수동 검증 항목:

1. EXE에서 우클릭 메뉴를 등록하고 실제 탐색기 하위 메뉴를 확인합니다.
2. 변환 결과가 원본 폴더에 생기는지, 체크 해제 후 메뉴가 제거되는지 확인합니다.
3. PowerPoint 또는 LibreOffice가 설치된 PC에서 PPT/PPTX → PDF와 PDF → PPT를 검증합니다.
4. Windows 배율 100%/150%, 한글 경로, 긴 파일명, 여러 입력 폴더를 확인합니다.
5. `--document-self-test`로 DOCX→PDF, PDF→DOCX, 왕복 및 스캔 PDF 출력을 확인합니다.

## GitHub Actions

`ci.yml`은 Windows에서 단위 테스트와 진단을 실행합니다. `build.yml`은 수동 실행으로 EXE를 빌드·검증하고 Actions 아티팩트에 보관합니다. 자동 공개 릴리스는 만들지 않습니다.
