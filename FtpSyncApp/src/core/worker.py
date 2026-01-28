import time
from PyQt5.QtCore import QThread, pyqtSignal
from core.ftp_client import FtpClient

class SyncWorker(QThread):
    log_signal = pyqtSignal(str)
    total_progress_signal = pyqtSignal(int)
    file_progress_signal = pyqtSignal(int)
    file_name_signal = pyqtSignal(str)
    count_signal = pyqtSignal(int, int)
    finished_signal = pyqtSignal(bool)
    time_signal = pyqtSignal(str)
    # [수정] 오버플로우 방지를 위해 object 사용
    plan_signal = pyqtSignal(object, object)
    byte_progress_signal = pyqtSignal(object)

    def __init__(self, ftp_config, local_path):
        super().__init__()
        self.ftp_config = ftp_config
        self.local_path = local_path
        self.client = FtpClient()
        self.success_count = 0
        self.fail_count = 0
        self.start_time = 0
        self.total_bytes_transferred = 0 # 누적 전송량

    def run(self):
        self.success_count = 0
        self.fail_count = 0
        self.total_bytes_transferred = 0
        self.start_time = time.time()
        try:
            self.log_signal.emit(f"Connecting to {self.ftp_config['host']}...")
            self.client.connect(self.ftp_config['host'], self.ftp_config['port'], self.ftp_config['user'], self.ftp_config['password'])
            self.client.sync_local_to_remote_mirror('/', self.local_path, callback=self.report_progress)
            self.client.close()
            elapsed = time.time() - self.start_time
            self.time_signal.emit(f"{elapsed:.2f}s")
            self.finished_signal.emit(True)
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")
            self.finished_signal.emit(False)

    def report_progress(self, msg, t_curr, t_max, f_curr=0, f_max=0, status=None):
        if status == 'plan':
            self.plan_signal.emit(t_max, f_max)
            return

        elapsed = time.time() - self.start_time
        mins, secs = divmod(int(elapsed), 60)
        self.time_signal.emit(f"{mins:02d}:{secs:02d}")

        # [변경] 누적 전송량 계산 (현재 파일 진행분 + 이전 완료 파일들)
        # 단일 스레드는 f_curr가 현재 파일의 진행 바이트이므로, 
        # 이를 통해 누적치를 UI에 보냅니다. (정확한 누적은 UI에서 관리하는게 쉬움)
        if "Downloading" in msg:
            # f_curr 정보를 그대로 UI에 토스
            self.byte_progress_signal.emit(f_curr)

        if status == 'success':
            self.success_count += 1
            self.count_signal.emit(self.success_count, self.fail_count)
        elif status == 'fail':
            self.fail_count += 1
            self.count_signal.emit(self.success_count, self.fail_count)
        
        if "Downloading" in msg:
            clean_name = msg.replace("Downloading ", "").replace("...", "").strip()
            self.file_name_signal.emit(clean_name)
            if f_curr > 0 and f_curr < f_max: pass
            else: self.log_signal.emit(msg)
        else:
            self.log_signal.emit(msg)

        if t_max > 0: self.total_progress_signal.emit(int((t_curr / t_max) * 100))
        if f_max > 0: self.file_progress_signal.emit(int((f_curr / f_max) * 100))
        else: self.file_progress_signal.emit(0)