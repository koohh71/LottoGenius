
import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from ui.login_window import LoginWindow

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
        # PyQt5 High DPI support
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
        
        app = QApplication(sys.argv)
        
        # 이제 LoginWindow가 메인 역할을 수행합니다.
        window = LoginWindow()
        window.show()

        sys.exit(app.exec_())
        
    except Exception as e:
        exception_hook(type(e), e, e.__traceback__)

if __name__ == "__main__":
    main()
