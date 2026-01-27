
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QTextEdit, 
    QLabel, QGraphicsDropShadowEffect
)
from qfluentwidgets import (
    LineEdit, PasswordLineEdit, PrimaryPushButton, PushButton,
    ProgressBar, InfoBar, Theme, setTheme, setThemeColor, 
    CardWidget, StrongBodyLabel, TitleLabel, CaptionLabel, BodyLabel
)
from qfluentwidgets import FluentIcon as FIF
from core.worker_multi import SyncWorkerMulti
from core.config_manager import ConfigManager

class DashboardMulti(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('FTP Sync [LAB: Multi-Thread]')
        self.setFixedSize(600, 850)
        
        setTheme(Theme.DARK)
        setThemeColor('#ff0055') # 실험용은 붉은색 테마
        
        self.setStyleSheet("""
            DashboardMulti { background-color: #1e1e1e; }
            QTextEdit { background-color: #262626; border: 1px solid #333; color: #888; font-family: Consolas; }
            ProgressBar { background-color: #333; border: none; border-radius: 2px; }
            ProgressBar::chunk { background-color: #ff0055; border-radius: 2px; }
        """)

        self.config_manager = ConfigManager()
        self.worker = None
        self.file_slots = []
        
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(35, 40, 35, 35)
        main.setSpacing(15)

        # Header
        head = QHBoxLayout()
        icon = QLabel("🧪")
        icon.setStyleSheet("font-size: 32px;")
        head.addWidget(icon)
        
        box = QVBoxLayout()
        t = TitleLabel("FTP Sync LAB", self)
        t.setStyleSheet("font-weight: bold; color: white;")
        s = CaptionLabel("Experimental Multi-Thread Engine", self)
        s.setStyleSheet("color: #ff5555;")
        box.addWidget(t)
        box.addWidget(s)
        head.addLayout(box)
        
        # Timer Display
        self.timer_label = QLabel("00:00", self)
        self.timer_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #ff0055;")
        head.addStretch(1)
        head.addWidget(self.timer_label)
        
        main.addLayout(head)

        # Input
        card = CardWidget(self)
        card.setStyleSheet("CardWidget { background-color: #2b2b2b; border: 1px solid #383; }")
        c_layout = QVBoxLayout(card)
        
        h_row = QHBoxLayout()
        self.host = LineEdit(self); self.host.setPlaceholderText("Host")
        self.port = LineEdit(self); self.port.setText("21"); self.port.setFixedWidth(60)
        h_row.addWidget(self.host); h_row.addWidget(self.port)
        c_layout.addLayout(h_row)
        
        u_row = QHBoxLayout()
        self.user = LineEdit(self); self.user.setPlaceholderText("User")
        self.pwd = PasswordLineEdit(self); self.pwd.setPlaceholderText("Pass")
        u_row.addWidget(self.user); u_row.addWidget(self.pwd)
        c_layout.addLayout(u_row)
        
        p_row = QHBoxLayout()
        self.path = LineEdit(self); self.path.setReadOnly(True)
        btn = PushButton("Browse", self, FIF.FOLDER)
        btn.clicked.connect(self.browse)
        p_row.addWidget(self.path); p_row.addWidget(btn)
        c_layout.addLayout(p_row)
        
        main.addWidget(card)

        # Start Button
        self.btn = PrimaryPushButton("START EXPERIMENT", self, FIF.GAME)
        self.btn.setFixedHeight(50)
        self.btn.clicked.connect(self.start)
        main.addWidget(self.btn)

        # Status
        self.cnt_lbl = StrongBodyLabel("Success: 0 | Fail: 0", self)
        self.cnt_lbl.setAlignment(Qt.AlignCenter)
        self.cnt_lbl.setStyleSheet("color: #ccc;")
        main.addWidget(self.cnt_lbl)
        
        self.total_bar = ProgressBar(self)
        self.total_bar.setFixedHeight(10)
        main.addWidget(self.total_bar)

        # Slots
        main.addWidget(CaptionLabel("Active Threads (4 Workers)", self))
        
        slot_box = QVBoxLayout()
        slot_box.setSpacing(8)
        for i in range(4):
            row = QHBoxLayout()
            l = CaptionLabel(f"Thread {i+1}: Idle", self)
            l.setFixedWidth(180)
            l.setStyleSheet("color: #666;")
            b = ProgressBar(self)
            b.setFixedHeight(6)
            row.addWidget(l); row.addWidget(b)
            slot_box.addLayout(row)
            self.file_slots.append((l, b))
        main.addLayout(slot_box)

        # Log
        self.log = QTextEdit(self)
        self.log.setReadOnly(True)
        main.addWidget(self.log)

    def load_settings(self):
        cfg = self.config_manager.load_config()
        self.host.setText(cfg.get('host', ''))
        self.port.setText(cfg.get('port', '21'))
        self.user.setText(cfg.get('user', ''))
        self.path.setText(cfg.get('local_path', ''))
        p = cfg.get('password_enc', '')
        if p: self.pwd.setText(self.config_manager.decode_password(p))

    def browse(self):
        d = QFileDialog.getExistingDirectory(self, "Select Folder")
        if d: self.path.setText(d)

    def start(self):
        self.btn.setEnabled(False)
        self.log.clear()
        self.timer_label.setText("00:00")
        
        # Reset Slots
        for l, b in self.file_slots:
            l.setText("Idle")
            b.setValue(0)
            
        cfg = {
            'host': self.host.text().strip(),
            'port': int(self.port.text().strip()),
            'user': self.user.text().strip(),
            'password': self.pwd.text().strip()
        }
        
        self.worker = SyncWorkerMulti(cfg, self.path.text())
        self.worker.log_signal.connect(self.log.append)
        self.worker.total_progress_signal.connect(self.total_bar.setValue)
        self.worker.multi_file_progress_signal.connect(self.update_slot)
        self.worker.count_signal.connect(lambda s, f: self.cnt_lbl.setText(f"Success: {s} | Fail: {f}"))
        self.worker.time_signal.connect(self.timer_label.setText)
        self.worker.finished_signal.connect(self.done)
        self.worker.start()

    def update_slot(self, idx, pct, name):
        if 0 <= idx < 4:
            lbl, bar = self.file_slots[idx]
            bar.setValue(pct)
            if name == "Done":
                lbl.setText("Completed")
                lbl.setStyleSheet("color: #00ff88;")
            else:
                lbl.setText(f"{name[:15]}.. ({pct}%)")
                lbl.setStyleSheet("color: #ff0055;")

    def done(self, ok):
        self.btn.setEnabled(True)
        if ok: InfoBar.success(title='Done', content='Experiment Completed.', parent=self)
        else: InfoBar.error(title='Error', content='Failed.', parent=self)
