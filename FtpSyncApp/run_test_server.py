import os
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

def start_server():
    # 1. 서버 저장소 폴더 생성 (여기에 직접 파일을 넣으세요!)
    remote_dir = "test_remote"
    if not os.path.exists(remote_dir):
        os.mkdir(remote_dir)
        print(f"📁 Created server directory: {os.path.abspath(remote_dir)}")
    
    print(f"📢 Put any files you want to test in: {os.path.abspath(remote_dir)}")

    # 2. 계정 설정
    authorizer = DummyAuthorizer()
    authorizer.add_user("test", "1234", os.path.abspath(remote_dir), perm="elradfmw")

    handler = FTPHandler
    handler.authorizer = authorizer
    handler.encoding = 'utf-8'

    try:
        server = FTPServer(("127.0.0.1", 2121), handler)
        print(
"""
=============================================
🚀 FTP Server is READY!
=============================================
  Host: 127.0.0.1 / Port: 2121
  User: test / Pass: 1234
=============================================
Waiting for sync request...

""")
        server.serve_forever()
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    start_server()