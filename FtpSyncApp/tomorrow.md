# 📅 내일의 작업 계획 (FtpSyncApp)

## 1. 새 PC 환경 설정 (Setup)
다른 PC에서 프로젝트를 가져온 후 다음 순서로 환경을 구축합니다.

1.  **프로젝트 내려받기:** `git clone <저장소주소>` 또는 압축 해제.
2.  **가상환경 생성:**
    ```powershell
    cd FtpSyncApp
    python -m venv venv
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process  # 스크립트 실행 권한 허용
    .\venv\Scripts\activate
    ```
3.  **의존성 설치:**
    ```powershell
    pip install -r requirements.txt
    ```

## 2. 기능 구현 현황 (Status)

### ✅ 완료된 기능
- [x] **설정 자동 저장:** `config.json`을 통해 호스트, 사용자, 경로 정보 영구 저장.
- [x] **정밀 진행률 표시:** 
    - 전체 파일 개수 기준 진행률 (%)
    - 개별 파일 전송률 (%, 파일명)
- [x] **고성능 엔진 (안정성):** 재접속(Retry), 원자적 쓰기(.tmp), 스마트 버퍼링 적용.
- [x] **멀티스레드 실험실:** `src/lab_multi_sync.py`를 통해 4개 파일 동시 다운로드 및 속도 비교 가능.
- [x] **전송 타이머:** 작업 소요 시간 실시간 측정 및 결과 표시.

## 3. 향후 과제 (To-Do)

### 🚀 멀티스레드 정식 통합
- [ ] 현재 `lab_multi_sync.py`에 있는 4-Slot 멀티 엔진을 메인 앱(`src/main.py`)에 정식 옵션으로 통합.
- [ ] 설정 화면에서 "싱글 스레드(안정형)" vs "멀티 스레드(고속형)" 선택 기능 추가.

### 📦 배포 및 패키징
- [ ] `PyInstaller`를 사용하여 아이콘이 포함된 단일 `.exe` 파일 생성.
    ```bash
    pyinstaller --noconsole --onefile src/main.py
    ```

### 📊 UX 고도화
- [ ] **남은 시간 예측 (ETA):** 전송 속도 기반으로 "약 3분 남음" 표시.
- [ ] **전송 속도 표시:** "5.2 MB/s" 등의 실시간 속도계 추가.

---
**💡 실행 가이드:**
- **안정 버전:** `python src/main.py`
- **멀티스레드 실험:** `python src/lab_multi_sync.py`
- **테스트 서버:** `python run_test_server.py`