import os
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QTextEdit
)
from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, SubtitleLabel, 
    PrimaryPushButton, LineEdit, PushButton, InfoBar, 
    FluentIcon as FIF, CardWidget
)
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
            self.log_signal.emit("Connecting to server...")
            self.client.connect(
                self.ftp_config['host'],
                self.ftp_config['port'],
                self.ftp_config['user'],
                self.ftp_config['password']
            )
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


class HomeInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("homeInterface")
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(30, 30, 30, 30)
        self.v_layout.setSpacing(20)

        self.title = SubtitleLabel(self)
        self.title.setText("Synchronization Dashboard")
        self.v_layout.addWidget(self.title)

        self.status_card = CardWidget(self)
        self.status_card.setFixedHeight(80)
        card_layout = QHBoxLayout(self.status_card)
        self.status_label = SubtitleLabel(self.status_card)
        self.status_label.setText("Ready to Sync")
        card_layout.addWidget(self.status_label)
        card_layout.addStretch(1)
        self.sync_btn = PrimaryPushButton(self.status_card)
        self.sync_btn.setText("Start Sync")
        self.sync_btn.setIcon(FIF.SYNC)
        card_layout.addWidget(self.sync_btn)
        self.v_layout.addWidget(self.status_card)

        self.log_view = QTextEdit(self)
        self.log_view.setReadOnly(True)
        self.log_view.setPlaceholderText("Logs will appear here...")
        self.v_layout.addWidget(self.log_view)

class SettingInterface(QWidget):
    pathChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("settingInterface")
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(30, 30, 30, 30)
        self.v_layout.setSpacing(20)
        
        self.title = SubtitleLabel(self)
        self.title.setText("Settings")
        self.v_layout.addWidget(self.title)

        h_layout = QHBoxLayout()
        self.path_edit = LineEdit(self)
        self.path_edit.setReadOnly(True)
        default_path = os.path.join(os.path.expanduser("~"), "Downloads", "FtpSync")
        self.path_edit.setText(default_path)
        
        self.browse_btn = PushButton(self)
        self.browse_btn.setText("Browse")
        self.browse_btn.setIcon(FIF.FOLDER)
        
        h_layout.addWidget(self.path_edit)
        h_layout.addWidget(self.browse_btn)
        self.v_layout.addLayout(h_layout)
        self.v_layout.addStretch(1)
        self.browse_btn.clicked.connect(self.browse_folder)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Local Sync Folder")
        if folder:
            self.path_edit.setText(folder)
            self.pathChanged.emit(folder)

    def get_local_path(self):
        return self.path_edit.text()


class MainWindow(FluentWindow):
    def __init__(self, ftp_config):
        super().__init__()
        self.ftp_config = ftp_config
        self.setWindowTitle('FTP Sync App')
        self.resize(800, 600)

        self.home_interface = HomeInterface(self)
        self.setting_interface = SettingInterface(self)

        self.addSubInterface(self.home_interface, FIF.HOME, 'Home')
        self.addSubInterface(self.setting_interface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM)
        
        self.home_interface.sync_btn.clicked.connect(self.start_sync)
        
    def start_sync(self):
        local_path = self.setting_interface.get_local_path()
        if not os.path.exists(local_path):
            os.makedirs(local_path)

        self.home_interface.sync_btn.setEnabled(False)
        self.home_interface.status_label.setText("Syncing...")
        self.home_interface.log_view.clear()
        
        self.worker = SyncWorker(self.ftp_config, local_path)
        self.worker.log_signal.connect(self.update_log)
        self.worker.finished_signal.connect(self.on_sync_finished)
        self.worker.start()

    def update_log(self, msg):
        self.home_interface.log_view.append(msg)

    def on_sync_finished(self, success):
        self.home_interface.sync_btn.setEnabled(True)
        if success:
            self.home_interface.status_label.setText("Sync Completed")
            InfoBar.success("Success", "Synchronization finished successfully.", parent=self.home_interface)
        else:
            self.home_interface.status_label.setText("Sync Failed")
            InfoBar.error("Error", "Synchronization failed. Check logs.", parent=self.home_interface)