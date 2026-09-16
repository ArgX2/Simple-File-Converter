# 공개 배포 준비

## 최초 공개 전

- 프로젝트 소유자가 공개 라이선스를 선택하고 루트에 `LICENSE`를 추가합니다.
- PyMuPDF/MuPDF, Qt, FFmpeg 등 외부 구성요소의 라이선스 조건을 확인합니다.
- `licenses/`는 현재 사용한 구성요소의 고지 기록입니다. 버전을 바꾸면 갱신합니다.
- 해당 배포물에 필요한 외부 소스/빌드 자료 제공 범위를 확인합니다. 고지 파일만으로 모든 배포 요건이 충족되는 것은 아닙니다.

## 릴리스 절차

1. README와 의존성 버전을 확인합니다.
2. Windows에서 자동 테스트를 통과시킵니다.
3. 실행 파일을 빌드하고 `--self-test`의 `report.json`이 `ok: true`인지 확인합니다.
4. 탐색기 메뉴와 Office 변환을 실제 사용자 세션에서 수동 점검합니다.
5. 변경 사항을 릴리스 설명에 기록합니다.
6. GitHub Releases에 EXE와 SHA-256 체크섬을 첨부합니다. EXE를 Git 소스 이력에 넣지 않습니다.

```powershell
Get-FileHash -Algorithm SHA256 ".\dist\Simple File Converter.exe"
```

CI 성공과 코드 서명은 별개입니다. 현재 빌드는 코드 서명되지 않습니다.
