
import time
from PyQt5.QtCore import QThread, pyqtSignal
from core.ftp_client_multi import FtpClientMulti

class SyncWorkerMulti(QThread):
    log_signal = pyqtSignal(str)
    total_progress_signal = pyqtSignal(int)
    multi_file_progress_signal = pyqtSignal(int, int, str) # slot, pct, name
    count_signal = pyqtSignal(int, int)
    finished_signal = pyqtSignal(bool)
    time_signal = pyqtSignal(str) # "00:12" 형태의 시간 문자열 전달

    def __init__(self, ftp_config, local_path):
        super().__init__()
        self.ftp_config = ftp_config
        self.local_path = local_path
        self.client = FtpClientMulti()
        self.success_count = 0
        self.fail_count = 0
        self.start_time = 0

    def run(self):
        self.success_count = 0
        self.fail_count = 0
        self.start_time = time.time()
        
        try:
            self.log_signal.emit(f"Connecting to {self.ftp_config['host']} (Multi-Thread)...")
            self.client.connect(
                self.ftp_config['host'],
                self.ftp_config['port'],
                self.ftp_config['user'],
                self.ftp_config['password']
            )
            
            self.client.sync_local_to_remote_mirror(
                '/', 
                self.local_path, 
                callback=self.report_progress
            )
            
            self.client.close()
            
            # 최종 시간 계산
            elapsed = time.time() - self.start_time
            self.time_signal.emit(f"{elapsed:.2f}s")
            self.finished_signal.emit(True)
            
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")
            self.finished_signal.emit(False)

    def report_progress(self, msg, t_curr, t_max, f_curr=0, f_max=0, status=None, slot_idx=-1):
        # 실시간 타이머 업데이트 (너무 자주는 아니고 가끔)
        elapsed = time.time() - self.start_time
        mins, secs = divmod(int(elapsed), 60)
        self.time_signal.emit(f"{mins:02d}:{secs:02d}")

        if status == 'success':
            self.success_count += 1
            self.count_signal.emit(self.success_count, self.fail_count)
        elif status == 'fail':
            self.fail_count += 1
            self.count_signal.emit(self.success_count, self.fail_count)
        
        if slot_idx >= 0:
            if "Downloading" in msg:
                pct = 0
                if f_max > 0: pct = int((f_curr / f_max) * 100)
                filename = msg.replace("Downloading ", "").replace("...", "").strip()
                self.multi_file_progress_signal.emit(slot_idx, pct, filename)
                return
            elif "Downloaded" in msg:
                self.multi_file_progress_signal.emit(slot_idx, 100, "Done")
                return

        self.log_signal.emit(msg)
        if t_max > 0:
            self.total_progress_signal.emit(int((t_curr / t_max) * 100))
