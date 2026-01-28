
import time
from PyQt5.QtCore import QThread, pyqtSignal
from core.ftp_client_multi import FtpClientMulti

class SyncWorkerMulti(QThread):
    log_signal = pyqtSignal(str)
    total_progress_signal = pyqtSignal(int)
    multi_file_progress_signal = pyqtSignal(int, int, str)
    count_signal = pyqtSignal(int, int)
    finished_signal = pyqtSignal(bool)
    time_signal = pyqtSignal(str)
    # [수정] 오버플로우 방지 (object)
    plan_signal = pyqtSignal(object, object)
    byte_progress_signal = pyqtSignal(object)

    def __init__(self, ftp_config, local_path):
        super().__init__()
        self.ftp_config = ftp_config
        self.local_path = local_path
        self.client = FtpClientMulti()
        self.success_count = 0
        self.fail_count = 0
        self.start_time = 0
        self.acc_bytes = 0 # 완료된 파일들의 총 바이트 합계

    def run(self):
        self.success_count = 0
        self.fail_count = 0
        self.acc_bytes = 0
        self.start_time = time.time()
        try:
            self.log_signal.emit(f"Connecting to {self.ftp_config['host']} (Multi-Thread)...")
            self.client.connect(self.ftp_config['host'], self.ftp_config['port'], self.ftp_config['user'], self.ftp_config['password'])
            self.client.sync_local_to_remote_mirror('/', self.local_path, callback=self.report_progress)
            self.client.close()
            elapsed = time.time() - self.start_time
            self.time_signal.emit(f"{elapsed:.2f}s")
            self.finished_signal.emit(True)
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")
            self.finished_signal.emit(False)

    def report_progress(self, msg, t_curr, t_max, f_curr=0, f_max=0, status=None, slot_idx=-1):
        if status == 'plan':
            self.plan_signal.emit(t_max, f_max)
            return

        elapsed = time.time() - self.start_time
        mins, secs = divmod(int(elapsed), 60)
        self.time_signal.emit(f"{mins:02d}:{secs:02d}")

        # 멀티스레드 바이트 추적
        if slot_idx >= 0:
            if status == 'success':
                self.acc_bytes += f_max # 파일 완료 시 크기 합산
                self.byte_progress_signal.emit(self.acc_bytes)
            
            if "Downloading" in msg:
                pct = 0
                if f_max > 0: pct = int((f_curr / f_max) * 100)
                filename = msg.replace("Downloading ", "").replace("...", "").strip()
                self.multi_file_progress_signal.emit(slot_idx, pct, filename)
                # (옵션) 실시간 전송 중인 바이트도 조금씩 합산하여 보낼 수 있으나 복잡하므로 완료 시점에 집중
                return
            elif "Downloaded" in msg:
                self.multi_file_progress_signal.emit(slot_idx, 100, "Done")
                return

        if status == 'success':
            self.success_count += 1
            self.count_signal.emit(self.success_count, self.fail_count)
        elif status == 'fail':
            self.fail_count += 1
            self.count_signal.emit(self.success_count, self.fail_count)

        self.log_signal.emit(msg)
        if t_max > 0:
            self.total_progress_signal.emit(int((t_curr / t_max) * 100))
