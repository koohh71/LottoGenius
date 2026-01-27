import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QTextEdit, 
    QLabel, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QColor
from qfluentwidgets import (
    LineEdit, PasswordLineEdit, PushButton, PrimaryPushButton,
    ProgressBar, InfoBar, InfoBarPosition, Theme, setTheme, 
    setThemeColor, CardWidget, StrongBodyLabel, TitleLabel,
    CaptionLabel, BodyLabel
)
from qfluentwidgets import FluentIcon as FIF
from core.worker import SyncWorker
from core.config_manager import ConfigManager

class SyncDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('FTP Sync Pro')
        self.setFixedSize(500, 800)
        
        setTheme(Theme.DARK)
        setThemeColor('#00e5ff')
        
        self.setStyleSheet("""
            SyncDashboard { background-color: #1e1e1e; }
            QTextEdit { 
                background-color: #262626; 
                border: 1px solid #333333; 
                border-radius: 4px; 
                color: #888888;
                font-family: 'Consolas', monospace;
                font-size: 10pt;
            }
        """)

        self.config_manager = ConfigManager()
        self.current_filename = ""
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(35, 40, 35, 35)
        main_layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        icon_label = QLabel("🚀") 
        icon_label.setStyleSheet("font-size: 32px;")
        header_layout.addWidget(icon_label)
        
        title_box = QVBoxLayout()
        title = TitleLabel("FTP Sync Pro", self)
        title.setStyleSheet("font-weight: bold; color: white;")
        subtitle = CaptionLabel("Secure File Mirroring System", self)
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)
        header_layout.addStretch(1)
        
        # [추가] 타이머 라벨
        self.timer_label = QLabel("00:00", self)
        self.timer_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff0055;")
        header_layout.addWidget(self.timer_label)
        
        main_layout.addLayout(header_layout)

        # Input Card
        self.input_card = CardWidget(self)
        self.input_card.setStyleSheet("CardWidget { background-color: #2b2b2b; border: 1px solid #383838; }")
        
        card_layout = QVBoxLayout(self.input_card)
        card_layout.setSpacing(12)

        self.host_edit = LineEdit(self)
        self.host_edit.setPlaceholderText('FTP Host Address')
        self.port_edit = LineEdit(self)
        self.port_edit.setText('21')
        self.port_edit.setFixedWidth(70)
        
        host_layout = QHBoxLayout()
        host_layout.addWidget(self.host_edit)
        host_layout.addWidget(self.port_edit)
        card_layout.addLayout(host_layout)

        self.user_edit = LineEdit(self)
        self.user_edit.setPlaceholderText('Username')
        self.pass_edit = PasswordLineEdit(self)
        self.pass_edit.setPlaceholderText('Password')
        
        user_layout = QHBoxLayout()
        user_layout.addWidget(self.user_edit)
        user_layout.addWidget(self.pass_edit)
        card_layout.addLayout(user_layout)

        path_layout = QHBoxLayout()
        self.path_edit = LineEdit(self)
        self.path_edit.setReadOnly(True)
        self.browse_btn = PushButton("Browse", self, FIF.FOLDER)
        self.browse_btn.clicked.connect(self.browse_folder)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_btn)
        card_layout.addLayout(path_layout)

        main_layout.addWidget(self.input_card)

        # Sync Button
        self.sync_btn = PrimaryPushButton("START SYNCHRONIZATION", self, FIF.SYNC)
        self.sync_btn.setFixedHeight(50)
        self.sync_btn.setStyleSheet("""
            PrimaryPushButton {
                background-color: #009faa;
                border: 2px solid #00e5ff;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            PrimaryPushButton:hover { background-color: #00c2d1; }
            PrimaryPushButton:pressed { background-color: #007a85; }
            PrimaryPushButton:disabled { background-color: #444444; border: 2px solid #555555; }
        """)
        self.sync_btn.clicked.connect(self.start_sync)
        main_layout.addWidget(self.sync_btn)

        main_layout.addSpacing(10)

        # Progress Section
        self.count_label = StrongBodyLabel("성공: 0  |  실패: 0", self)
        self.count_label.setAlignment(Qt.AlignCenter)
        self.count_label.setStyleSheet("color: #cccccc; font-size: 14px; margin-bottom: 5px;")
        main_layout.addWidget(self.count_label)

        self.total_info_label = BodyLabel("전체 진행율 : 0%", self)
        self.total_info_label.setStyleSheet("color: white; font-weight: bold;")
        main_layout.addWidget(self.total_info_label)
        
        self.total_bar = ProgressBar(self)
        self.total_bar.setFixedHeight(12)
        self.total_bar.setValue(0)
        main_layout.addWidget(self.total_bar)

        main_layout.addSpacing(5)

        self.file_info_label = CaptionLabel("대기 중...", self)
        self.file_info_label.setStyleSheet("color: #00e5ff;")
        main_layout.addWidget(self.file_info_label)
        
        self.file_bar = ProgressBar(self)
        self.file_bar.setFixedHeight(6)
        self.file_bar.setValue(0)
        main_layout.addWidget(self.file_bar)

        # Log
        self.log_view = QTextEdit(self)
        self.log_view.setReadOnly(True)
        main_layout.addWidget(self.log_view)

    def load_settings(self):
        cfg = self.config_manager.load_config()
        self.host_edit.setText(cfg.get('host', ''))
        self.port_edit.setText(cfg.get('port', '21'))
        self.user_edit.setText(cfg.get('user', ''))
        self.path_edit.setText(cfg.get('local_path', ''))
        enc_pwd = cfg.get('password_enc', '')
        if enc_pwd:
            self.pass_edit.setText(self.config_manager.decode_password(enc_pwd))

    def save_current_settings(self):
        self.config_manager.save_config(
            self.host_edit.text().strip(),
            self.port_edit.text().strip(),
            self.user_edit.text().strip(),
            self.pass_edit.text().strip(),
            self.path_edit.text().strip()
        )

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder: self.path_edit.setText(folder)

    def start_sync(self):
        self.save_current_settings()
        self.input_card.setEnabled(False)
        self.sync_btn.setEnabled(False)
        self.log_view.clear()
        self.timer_label.setText("00:00")
        
        self.count_label.setText("성공: 0  |  실패: 0")
        self.count_label.setStyleSheet("color: #cccccc; font-size: 14px; margin-bottom: 5px;")
        
        ftp_config = {
            'host': self.host_edit.text().strip(),
            'port': int(self.port_edit.text().strip()),
            'user': self.user_edit.text().strip(),
            'password': self.pass_edit.text().strip()
        }

        self.worker = SyncWorker(ftp_config, self.path_edit.text())
        self.worker.log_signal.connect(self.log_view.append)
        self.worker.total_progress_signal.connect(self.update_total_progress)
        self.worker.file_name_signal.connect(self.update_file_name)
        self.worker.file_progress_signal.connect(self.update_file_progress)
        self.worker.count_signal.connect(self.update_count)
        # 타이머 연결
        self.worker.time_signal.connect(self.timer_label.setText)
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.start()

    def update_total_progress(self, val):
        self.total_bar.setValue(val)
        self.total_info_label.setText(f"전체 진행율 : {val}%")

    def update_file_name(self, name):
        self.current_filename = name
        self.file_info_label.setText(f"현재 파일 : {name} (0%)")

    def update_file_progress(self, val):
        self.file_bar.setValue(val)
        if self.current_filename:
            self.file_info_label.setText(f"현재 파일 : {self.current_filename} ({val}%)")

    def update_count(self, success, fail):
        if fail > 0: color_style = "color: #ff5555;"
        else: color_style = "color: #00ff88;"
        self.count_label.setText(f"성공: {success}  |  실패: {fail}")
        self.count_label.setStyleSheet(f"{color_style} font-size: 14px; font-weight: bold; margin-bottom: 5px;")

    def on_finished(self, success):
        self.input_card.setEnabled(True)
        self.sync_btn.setEnabled(True)
        if success:
            self.total_info_label.setText("전체 진행율 : 100% (완료)")
            self.file_info_label.setText("모든 작업이 완료되었습니다.")
            InfoBar.success(title='완료', content='동기화 작업이 끝났습니다.', parent=self)
        else:
            self.total_info_label.setText("동기화 중단")
            InfoBar.error(title='오류', content='작업 중 문제가 발생했습니다.', parent=self)