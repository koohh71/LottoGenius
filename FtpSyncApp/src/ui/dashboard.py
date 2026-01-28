import os
import time
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QTextEdit, 
    QLabel, QGraphicsDropShadowEffect, QCheckBox, QFrame
)
from PyQt5.QtGui import QColor
from qfluentwidgets import (
    LineEdit, PasswordLineEdit, PushButton, PrimaryPushButton,
    ProgressBar, InfoBar, InfoBarPosition, Theme, setTheme, 
    setThemeColor, CardWidget, StrongBodyLabel, TitleLabel,
    CaptionLabel, BodyLabel, CheckBox
)
from qfluentwidgets import FluentIcon as FIF
from core.worker import SyncWorker
from core.worker_multi import SyncWorkerMulti
from core.config_manager import ConfigManager

class SyncDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('FTP Sync Pro')
        self.setFixedSize(550, 900)
        
        setTheme(Theme.DARK)
        setThemeColor('#00e5ff')
        
        self.setStyleSheet("""
            SyncDashboard { background-color: #1e1e1e; }
            QTextEdit { 
                background-color: #262626; border: 1px solid #333333; 
                border-radius: 4px; color: #888888;
                font-family: 'Consolas', monospace; font-size: 10pt;
            }
            ProgressBar { background-color: #333333; border: none; border-radius: 2px; }
            ProgressBar::chunk { background-color: #00e5ff; border-radius: 2px; }
        """)

        self.config_manager = ConfigManager()
        self.worker = None
        self.file_slots = [] 
        
        self.total_bytes_to_transfer = 0
        self.bytes_transferred_so_far = 0
        self.start_timestamp = 0
        
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(35, 40, 35, 35)
        main_layout.setSpacing(12)

        # Header
        header_layout = QHBoxLayout()
        icon_label = QLabel("🚀"); icon_label.setStyleSheet("font-size: 32px;"); header_layout.addWidget(icon_label)
        title_box = QVBoxLayout()
        title = TitleLabel("FTP Sync Pro", self); title.setStyleSheet("font-weight: bold; color: white;")
        subtitle = CaptionLabel("Secure File Mirroring System", self); title_box.addWidget(title); title_box.addWidget(subtitle)
        header_layout.addLayout(title_box); header_layout.addStretch(1)
        self.timer_label = QLabel("00:00", self); self.timer_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff0055;")
        header_layout.addWidget(self.timer_label)
        main_layout.addLayout(header_layout)

        # Input Card
        self.input_card = CardWidget(self)
        self.input_card.setStyleSheet("CardWidget { background-color: #2b2b2b; border: 1px solid #383838; }")
        card_layout = QVBoxLayout(self.input_card)
        
        row1 = QHBoxLayout(); self.host_edit = LineEdit(self); self.host_edit.setPlaceholderText('FTP Host Address')
        self.port_edit = LineEdit(self); self.port_edit.setText('21'); self.port_edit.setFixedWidth(70)
        row1.addWidget(self.host_edit); row1.addWidget(self.port_edit); card_layout.addLayout(row1)
        
        row2 = QHBoxLayout(); self.user_edit = LineEdit(self); self.user_edit.setPlaceholderText('Username')
        self.pass_edit = PasswordLineEdit(self); self.pass_edit.setPlaceholderText('Password')
        row2.addWidget(self.user_edit); row2.addWidget(self.pass_edit); card_layout.addLayout(row2)
        
        row3 = QHBoxLayout(); self.path_edit = LineEdit(self); self.path_edit.setReadOnly(True)
        self.browse_btn = PushButton("Browse", self, FIF.FOLDER); self.browse_btn.clicked.connect(self.browse_folder)
        row3.addWidget(self.path_edit); row3.addWidget(self.browse_btn); card_layout.addLayout(row3)
        
        self.multi_check = CheckBox("Enable High-Speed Mode (Multi-Thread)", self); self.multi_check.setChecked(True)
        self.multi_check.stateChanged.connect(self.toggle_mode_ui); card_layout.addWidget(self.multi_check)
        main_layout.addWidget(self.input_card)

        # Sync Button
        self.sync_btn = PrimaryPushButton("START SYNCHRONIZATION", self, FIF.SYNC)
        self.sync_btn.setFixedHeight(50); self.sync_btn.clicked.connect(self.start_sync)
        main_layout.addWidget(self.sync_btn)

        # Progress
        self.count_label = StrongBodyLabel("성공: 0  |  실패: 0", self)
        self.count_label.setAlignment(Qt.AlignCenter); self.count_label.setStyleSheet("color: #cccccc; font-size: 14px;")
        main_layout.addWidget(self.count_label)

        # [변경] 통합된 전체 진행률 라벨
        self.total_info_label = BodyLabel("전체 진행율 : 0%", self)
        self.total_info_label.setStyleSheet("color: white; font-weight: bold;")
        main_layout.addWidget(self.total_info_label)
        
        self.total_bar = ProgressBar(self); self.total_bar.setFixedHeight(12); main_layout.addWidget(self.total_bar)

        # Slots
        self.single_progress_widget = QWidget(); single_layout = QVBoxLayout(self.single_progress_widget)
        # [변경] 현재 파일 -> 다운로드
        self.file_info_label = CaptionLabel("대기 중...", self); self.file_bar = ProgressBar(self); self.file_bar.setFixedHeight(6)
        single_layout.addWidget(self.file_info_label); single_layout.addWidget(self.file_bar); main_layout.addWidget(self.single_progress_widget)

        self.multi_slots_widget = QWidget(); multi_layout = QVBoxLayout(self.multi_slots_widget)
        # [변경] Active Threads 라벨 제거
        for i in range(4):
            row = QHBoxLayout()
            # [변경] Thread 1 -> 다운로드 1
            l = CaptionLabel(f"다운로드 {i+1}: 대기", self); l.setFixedWidth(180)
            b = ProgressBar(self); b.setFixedHeight(6); b.setValue(0)
            row.addWidget(l); row.addWidget(b); multi_layout.addLayout(row); self.file_slots.append((l, b))
        main_layout.addWidget(self.multi_slots_widget)

        self.log_view = QTextEdit(self); self.log_view.setReadOnly(True); main_layout.addWidget(self.log_view)
        self.toggle_mode_ui()

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder: self.path_edit.setText(folder)

    def toggle_mode_ui(self):
        is_multi = self.multi_check.isChecked()
        self.multi_slots_widget.setVisible(is_multi); self.single_progress_widget.setVisible(not is_multi)

    def format_size(self, size_bytes):
        if size_bytes == 0: return "0 B"
        units = ("B", "KB", "MB", "GB", "TB"); i = 0; s = float(size_bytes)
        while s >= 1024 and i < len(units) - 1: s /= 1024; i += 1
        if i == 0: return f"{int(s)} {units[i]}"
        return f"{s:.2f} {units[i]}"

    def load_settings(self):
        cfg = self.config_manager.load_config()
        self.host_edit.setText(cfg.get('host', '')); self.port_edit.setText(cfg.get('port', '21'))
        self.user_edit.setText(cfg.get('user', '')); self.path_edit.setText(cfg.get('local_path', ''))
        p = cfg.get('password_enc', ''); 
        if p: self.pass_edit.setText(self.config_manager.decode_password(p))

    def start_sync(self):
        self.config_manager.save_config(self.host_edit.text(), self.port_edit.text(), self.user_edit.text(), self.pass_edit.text(), self.path_edit.text())
        self.input_card.setEnabled(False); self.sync_btn.setEnabled(False); self.log_view.clear(); self.timer_label.setText("00:00")
        self.total_bytes_to_transfer = 0; self.bytes_transferred_so_far = 0; self.start_timestamp = 0
        self.total_info_label.setText("파일 분석 중...")
        
        ftp_cfg = {'host': self.host_edit.text().strip(), 'port': int(self.port_edit.text().strip()), 'user': self.user_edit.text().strip(), 'password': self.pass_edit.text().strip()}
        is_multi = self.multi_check.isChecked()
        self.worker = SyncWorkerMulti(ftp_cfg, self.path_edit.text()) if is_multi else SyncWorker(ftp_cfg, self.path_edit.text())
        
        if is_multi: self.worker.multi_file_progress_signal.connect(self.update_slot_progress)
        else: self.worker.file_name_signal.connect(self.update_single_filename); self.worker.file_progress_signal.connect(self.update_single_progress)

        self.worker.log_signal.connect(self.log_view.append)
        self.worker.total_progress_signal.connect(self.update_total_progress)
        self.worker.count_signal.connect(self.update_count)
        self.worker.time_signal.connect(self.timer_label.setText)
        self.worker.finished_signal.connect(self.on_finished)
        try: self.worker.plan_signal.connect(self.on_plan_received)
        except: pass
        self.worker.byte_progress_signal.connect(self.update_stats)

        self.worker.start()

    def on_plan_received(self, file_count, total_bytes):
        self.total_bytes_to_transfer = total_bytes
        self.start_timestamp = time.time()
        # 초기 텍스트 세팅
        self.update_total_label(0)

    def update_stats(self, current_bytes):
        self.bytes_transferred_so_far = current_bytes
        # 여기서는 라벨 갱신을 위해 별도 동작 필요 없음 (update_total_progress에서 함)
        # 만약 진행률(%)이 안 변해도 바이트는 변할 수 있으니 즉시 갱신
        self.update_total_label(self.total_bar.value())

    def update_total_progress(self, val):
        self.total_bar.setValue(val)
        self.update_total_label(val)

    def update_total_label(self, pct):
        # 전체 진행율 : 79% (다운량/전체량)
        curr_str = self.format_size(self.bytes_transferred_so_far)
        total_str = self.format_size(self.total_bytes_to_transfer)
        self.total_info_label.setText(f"전체 진행율 : {pct}% ({curr_str} / {total_str})")

    def update_single_filename(self, name): self.file_info_label.setText(f"다운로드: {name}")
    def update_single_progress(self, val): self.file_bar.setValue(val)

    def update_slot_progress(self, idx, pct, filename):
        if 0 <= idx < 4:
            lbl, bar = self.file_slots[idx]; bar.setValue(pct)
            if filename == "Done": lbl.setText(f"다운로드 {idx+1}: 완료"); lbl.setStyleSheet("color: #00ff88;")
            else: lbl.setText(f"{filename[:15]}.. ({pct}%)"); lbl.setStyleSheet("color: #00e5ff;")

    def update_count(self, s, f):
        c = "#ff5555" if f > 0 else "#00ff88"
        self.count_label.setText(f"성공: {s}  |  실패: {f}"); self.count_label.setStyleSheet(f"color: {c}; font-size: 14px; font-weight: bold;")

    def on_finished(self, success):
        self.input_card.setEnabled(True); self.sync_btn.setEnabled(True)
        if success: 
            # 완료 시 최종 바이트로 표시
            total_str = self.format_size(self.total_bytes_to_transfer)
            self.total_info_label.setText(f"전체 진행율 : 100% ({total_str} / {total_str})")
            InfoBar.success(title='완료', content='동기화 성공.', parent=self)
        else: InfoBar.error(title='오류', content='작업 실패.', parent=self)