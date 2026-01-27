import os
import ftplib
import logging
from datetime import datetime, timezone

class FtpClient:
    def __init__(self):
        self.ftp = ftplib.FTP()
        self.encoding = 'utf-8'
        self.logger = logging.getLogger(__name__)

    def _parse_ftp_time(self, ftp_time_str):
        if not ftp_time_str:
            return 0
        try:
            dt = datetime.strptime(ftp_time_str[:14], "%Y%m%d%H%M%S")
            return dt.replace(tzinfo=timezone.utc).timestamp()
        except Exception:
            return 0

    def connect(self, host, port, user, password):
        try:
            self.ftp.connect(host, int(port))
            self.ftp.login(user, password)
            self.ftp.encoding = self.encoding
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            raise e

    def list_files_recursive(self, remote_dir):
        file_map = {}
        self._walk_ftp(remote_dir, "", file_map)
        return file_map

    def _walk_ftp(self, current_abs_path, relative_prefix, file_map):
        try:
            self.ftp.cwd(current_abs_path)
            items = list(self.ftp.mlsd())
            for name, facts in items:
                if name in ('.', '..'): continue
                
                # [수정] os.sep을 사용하여 안전하게 구분자 치환
                rel_path = os.path.join(relative_prefix, name).replace(os.sep, "/")
                
                if facts['type'] == 'dir':
                    file_map[rel_path] = {'type': 'dir', 'size': 0}
                    self._walk_ftp(f"{current_abs_path}/{name}", rel_path, file_map)
                else:
                    size = int(facts.get('size', 0))
                    mtime = facts.get('modify', '') 
                    file_map[rel_path] = {'type': 'file', 'size': size, 'mtime': mtime}
        except Exception as e:
            self.logger.error(f"Error walking FTP {current_abs_path}: {e}")

    def sync_local_to_remote_mirror(self, remote_root, local_root, callback=None):
        if callback: callback("Analyzing files (Size & Time)...")
        
        remote_files = self.list_files_recursive(remote_root)
        local_files = self._scan_local(local_root)

        to_download = []
        to_delete = []
        to_create_dir = []

        for rel_path, r_info in remote_files.items():
            if r_info['type'] == 'dir':
                if rel_path not in local_files:
                    to_create_dir.append(rel_path)
                continue

            if rel_path not in local_files:
                to_download.append(rel_path)
            else:
                l_info = local_files[rel_path]
                size_match = (l_info['size'] == r_info['size'])
                r_ts = self._parse_ftp_time(r_info['mtime'])
                l_ts = l_info['mtime']
                time_match = abs(r_ts - l_ts) < 2 if r_ts > 0 else True

                if not size_match or not time_match:
                    to_download.append(rel_path)
                else:
                    if callback: callback(f"Skipping {rel_path} (Matches)")

        for rel_path in local_files:
            if rel_path not in remote_files:
                to_delete.append(rel_path)

        for rel_path in to_delete:
            if callback: callback(f"Deleting {rel_path}...")
            p = os.path.join(local_root, rel_path)
            if os.path.isdir(p): 
                import shutil
                shutil.rmtree(p, ignore_errors=True)
            else:
                try: os.remove(p)
                except: pass

        for rel_path in to_create_dir:
            os.makedirs(os.path.join(local_root, rel_path), exist_ok=True)

        for rel_path in to_download:
            if callback: callback(f"Downloading {rel_path}...")
            local_path = os.path.join(local_root, rel_path)
            remote_abs_path = f"{remote_root}/{rel_path}".replace("//", "/")
            
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            try:
                with open(local_path, 'wb') as f:
                    self.ftp.retrbinary(f"RETR {remote_abs_path}", f.write)
                
                r_ts = self._parse_ftp_time(remote_files[rel_path]['mtime'])
                if r_ts > 0:
                    os.utime(local_path, (r_ts, r_ts))
            except Exception as e:
                if callback: callback(f"Failed {rel_path}: {e}")

        if callback: callback("Sync completed.")
        return True

    def _scan_local(self, local_root):
        local_map = {}
        for root, dirs, files in os.walk(local_root):
            for d in dirs:
                # [수정] os.sep 사용
                rel = os.path.relpath(os.path.join(root, d), local_root).replace(os.sep, "/")
                local_map[rel] = {'type': 'dir', 'size': 0}
            for f in files:
                abs_p = os.path.join(root, f)
                # [수정] os.sep 사용
                rel = os.path.relpath(abs_p, local_root).replace(os.sep, "/")
                local_map[rel] = {
                    'type': 'file', 
                    'size': os.path.getsize(abs_p), 
                    'mtime': os.path.getmtime(abs_p)
                }
        return local_map

    def close(self):
        try: self.ftp.quit()
        except: self.ftp.close()