import os
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

def start_server():
    # 1. 서버 저장소 폴더 (직접 파일을 넣을 수 있는 곳)
    remote_dir = "test_remote"
    if not os.path.exists(remote_dir):
        os.mkdir(remote_dir)
        print(f"📁 Server Root: {os.path.abspath(remote_dir)}")

    # 2. 계정 설정 (ID: test / PW: 1234)
    authorizer = DummyAuthorizer()
    authorizer.add_user("test", "1234", os.path.abspath(remote_dir), perm="elradfmw")

    handler = FTPHandler
    handler.authorizer = authorizer
    handler.encoding = 'utf-8'

    # 3. 서버 시작 (고속 모드)
    try:
        server = FTPServer(("127.0.0.1", 2121), handler)
        print("\n" + "="*45)
        print("🚀 FTP Server is RESTORED (Full Speed)!")
        print("="*45)
        print("  Host: 127.0.0.1 / Port: 2121")
        print("  User: test / Pass: 1234")
        print("="*45)
        server.serve_forever()
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    start_server()