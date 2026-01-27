
# 📅 내일의 작업 계획 (FtpSyncApp)

## 1. 새 PC 환경 설정 (Setup)
다른 PC에서 프로젝트를 가져온 후 다음 순서로 환경을 구축합니다.

1.  **프로젝트 내려받기:** `git clone <저장소주소>` 또는 압축 해제.
2.  **가상환경 생성:**
    ```powershell
    cd FtpSyncApp
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  **의존성 설치:**
    ```powershell
    pip install -r requirements.txt
    ```

## 2. 주요 개선 과제 (To-Do)

### ✅ 설정 자동 저장 기능 (Persistence)
- [ ] 마지막으로 입력한 FTP 호스트, 포트, 사용자 ID, 로컬 경로를 `config.json`에 저장.
- [ ] 앱 실행 시 저장된 설정을 자동으로 불러와서 입력 필드에 채우기.

### ✅ 실시간 진행률 정밀화 (Progress UI)
- [ ] 현재 5%씩 올라가는 더미 게이지를 **(전송된 파일 수 / 전체 파일 수)** 비율로 정확히 표시.
- [ ] 대용량 파일의 경우 파일 내부 전송률(Byte 단위) 표시 검토.

### ✅ 안정성 및 예외 처리
- [ ] 동기화 도중 네트워크가 끊겼을 때 앱이 튕기지 않도록 `Try-Except` 보강.
*   [ ] "연결 시도 중...", "서버 응답 없음" 등 상태 메시지 세분화.

### ✅ 배포 준비
- [ ] `PyInstaller`를 사용하여 아이콘이 포함된 단일 `.exe` 파일 생성 테스트.

---
**💡 팁:** 작업 시작 전 `python run_test_server.py`를 먼저 실행하여 로컬 환경에서 테스트가 가능한지 확인하세요!
