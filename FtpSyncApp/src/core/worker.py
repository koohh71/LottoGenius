
from PyQt5.QtCore import QThread, pyqtSignal
from core.ftp_client import FtpClient

class SyncWorker(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)

    def __init__(self, ftp_config, local_path):
        super().__init__()
        self.ftp_config = ftp_config
        self.local_path = local_path
        self.client = FtpClient()

    def run(self):
        try:
            self.log_signal.emit(f"Connecting to {self.ftp_config['host']}...")
            self.client.connect(
                self.ftp_config['host'],
                self.ftp_config['port'],
                self.ftp_config['user'],
                self.ftp_config['password']
            )
            
            # 원격지 루트 폴더('/')를 로컬 폴더와 동기화
            remote_root = '/' 
            
            self.client.sync_local_to_remote_mirror(
                remote_root, 
                self.local_path, 
                callback=self.emit_log
            )
            self.client.close()
            self.finished_signal.emit(True)
            
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")
            self.finished_signal.emit(False)

    def emit_log(self, msg):
        self.log_signal.emit(msg)
