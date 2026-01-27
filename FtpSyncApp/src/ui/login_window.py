
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QTextEdit
from qfluentwidgets import (
    LineEdit, PasswordLineEdit, PushButton, SubtitleLabel, 
    ProgressBar, InfoBar, InfoBarPosition, Theme, setTheme, 
    setThemeColor
)
from qfluentwidgets import FluentIcon as FIF
from core.worker import SyncWorker

class LoginWindow(QWidget):
    """ One-Click FTP Sync Window """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('FTP Sync App')
        self.resize(450, 600)
        
        # Theme & Color
        setTheme(Theme.DARK)
        setThemeColor('#009faa')
        self.setStyleSheet("LoginWindow { background-color: #272727; }")

        self.worker = None
        self.init_ui()

    def init_ui(self):
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(40, 40, 40, 40)
        self.v_layout.setSpacing(15)

        # 1. Title
        self.title_label = SubtitleLabel(self)
        self.title_label.setText('FTP Auto Sync')
        self.title_label.setAlignment(Qt.AlignCenter)
        self.v_layout.addWidget(self.title_label)

        self.v_layout.addSpacing(20)

        # 2. Connection Inputs
        # Host & Port
        h_layout = QHBoxLayout()
        self.host_edit = LineEdit(self)
        self.host_edit.setPlaceholderText('Host IP')
        
        self.port_edit = LineEdit(self)
        self.port_edit.setPlaceholderText('Port')
        self.port_edit.setText('21')
        self.port_edit.setFixedWidth(80)
        
        h_layout.addWidget(self.host_edit)
        h_layout.addWidget(self.port_edit)
        self.v_layout.addLayout(h_layout)

        # User
        self.user_edit = LineEdit(self)
        self.user_edit.setPlaceholderText('Username')
        self.v_layout.addWidget(self.user_edit)

        # Password
        self.pass_edit = PasswordLineEdit(self)
        self.pass_edit.setPlaceholderText('Password')
        self.v_layout.addWidget(self.pass_edit)

        # 3. Local Path Selection
        path_layout = QHBoxLayout()
        self.path_edit = LineEdit(self)
        self.path_edit.setPlaceholderText('Local Save Path')
        self.path_edit.setReadOnly(True)
        # Default path
        default_path = os.path.join(os.path.expanduser("~"), "Downloads", "FtpSync")
        self.path_edit.setText(default_path)
        
        self.browse_btn = PushButton(self)
        self.browse_btn.setText("Path")
        self.browse_btn.setIcon(FIF.FOLDER)
        self.browse_btn.setFixedWidth(80)
        self.browse_btn.clicked.connect(self.browse_folder)
        
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_btn)
        self.v_layout.addLayout(path_layout)

        self.v_layout.addSpacing(10)

        # 4. Action Button
        self.sync_btn = PushButton(self)
        self.sync_btn.setText('Connect & Start Sync')
        self.sync_btn.setIcon(FIF.SYNC)
        self.sync_btn.clicked.connect(self.start_sync)
        self.v_layout.addWidget(self.sync_btn)

        self.v_layout.addSpacing(20)

        # 5. Status & Logs
        self.status_label = SubtitleLabel(self)
        self.status_label.setText('Ready')
        self.status_label.setStyleSheet("font-size: 14px; color: #cccccc;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.v_layout.addWidget(self.status_label)
        
        self.progress_bar = ProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.hide() # Show when syncing
        self.v_layout.addWidget(self.progress_bar)

        self.log_view = QTextEdit(self)
        self.log_view.setReadOnly(True)
        self.log_view.setPlaceholderText("Logs will appear here...")
        self.log_view.setStyleSheet("background-color: #333333; border-radius: 5px; padding: 5px;")
        self.v_layout.addWidget(self.log_view)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.path_edit.setText(folder)

    def start_sync(self):
        host = self.host_edit.text().strip()
        port = self.port_edit.text().strip()
        user = self.user_edit.text().strip()
        password = self.pass_edit.text().strip()
        local_path = self.path_edit.text().strip()

        if not host or not user or not password:
            InfoBar.warning(
                title='Missing Info',
                content='Please fill in all fields.',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            return
        
        if not os.path.exists(local_path):
            os.makedirs(local_path)

        # UI Update
        self.sync_btn.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setValue(0) # Indeterminate state if needed
        self.log_view.clear()
        self.status_label.setText("Connecting...")

        # Worker Config
        ftp_config = {
            'host': host,
            'port': int(port),
            'user': user,
            'password': password
        }

        self.worker = SyncWorker(ftp_config, local_path)
        self.worker.log_signal.connect(self.update_log)
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.start()

    def update_log(self, msg):
        self.log_view.append(msg)
        # Update progress bar simply for activity indication
        current = self.progress_bar.value()
        if current < 90:
            self.progress_bar.setValue(current + 5)
        
        if "Downloading" in msg:
            self.status_label.setText("Downloading Files...")
        elif "Deleting" in msg:
            self.status_label.setText("Cleaning up...")

    def on_finished(self, success):
        self.sync_btn.setEnabled(True)
        self.progress_bar.setValue(100)
        
        if success:
            self.status_label.setText("Sync Completed Successfully")
            InfoBar.success(
                title='Success',
                content='All files are synced.',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        else:
            self.status_label.setText("Sync Failed")
            InfoBar.error(
                title='Error',
                content='Connection or Sync failed. Check logs.',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
