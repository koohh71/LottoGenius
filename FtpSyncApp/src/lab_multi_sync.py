import sys
import os

# 현재 파일의 위치를 기준으로 임포트 경로 조정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.dashboard_multi import DashboardMulti

def main():
    try:
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
        
        app = QApplication(sys.argv)
        
        window = DashboardMulti()
        window.show()

        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()