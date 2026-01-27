import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
# [변경] login_window 대신 dashboard 사용
from ui.dashboard import SyncDashboard

def exception_hook(exctype, value, tb):
    error_msg = "".join(traceback.format_exception(exctype, value, tb))
    print(error_msg)
    with open("crash_log.txt", "w", encoding="utf-8") as f:
        f.write(error_msg)
    try:
        if QApplication.instance():
            QMessageBox.critical(None, "Critical Error", f"An error occurred:\n{value}")
    except:
        pass
    sys.exit(1)

sys.excepthook = exception_hook

def main():
    try:
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
        
        app = QApplication(sys.argv)
        
        # Dashboard 로드
        window = SyncDashboard()
        window.show()

        sys.exit(app.exec_())
        
    except Exception as e:
        exception_hook(type(e), e, e.__traceback__)

if __name__ == "__main__":
    main()