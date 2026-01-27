import os
import time
import ftplib
import socket
import logging
from datetime import datetime, timezone

class FtpClient:
    def __init__(self):
        self.ftp = None
        self.host = None
        self.port = 21
        self.user = None
        self.password = None
        self.encoding = 'utf-8'
        self.logger = logging.getLogger(__name__)
        self.max_retries = 3
        self.retry_delay = 2

    def _parse_ftp_time(self, ftp_time_str):
        if not ftp_time_str: return 0
        try:
            dt = datetime.strptime(ftp_time_str[:14], "%Y%m%d%H%M%S")
            return dt.replace(tzinfo=timezone.utc).timestamp()
        except Exception: return 0

    def connect(self, host, port, user, password):
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password
        self._establish_connection()

    def _establish_connection(self):
        last_error = None
        for attempt in range(self.max_retries):
            try:
                if self.ftp:
                    try: self.ftp.quit()
                    except: pass
                self.ftp = ftplib.FTP()
                self.ftp.connect(self.host, self.port, timeout=30)
                self.ftp.login(self.user, self.password)
                self.ftp.encoding = self.encoding
                return True
            except (socket.error, ftplib.all_errors) as e:
                last_error = e
                time.sleep(self.retry_delay)
        raise ConnectionError(f"Failed to connect: {last_error}")

    def list_files_recursive(self, remote_dir):
        file_map = {}
        self._walk_ftp(remote_dir, "", file_map)
        return file_map

    def _walk_ftp(self, current_abs_path, relative_prefix, file_map):
        self.ftp.cwd(current_abs_path)
        items = list(self.ftp.mlsd())
        for name, facts in items:
            if name in ('.', '..'): continue
            rel_path = os.path.join(relative_prefix, name).replace(os.sep, "/")
            if facts['type'] == 'dir':
                file_map[rel_path] = {'type': 'dir', 'size': 0}
                self._walk_ftp(f"{current_abs_path}/{name}", rel_path, file_map)
            else:
                file_map[rel_path] = {
                    'type': 'file', 
                    'size': int(facts.get('size', 0)), 
                    'mtime': facts.get('modify', '')
                }

    def sync_local_to_remote_mirror(self, remote_root, local_root, callback=None):
        def report(msg, t_curr, t_max, f_curr=0, f_max=0, status=None):
            if callback: callback(msg, t_curr, t_max, f_curr, f_max, status)

        report("Analyzing files...", 0, 100)
        remote_files = self.list_files_recursive(remote_root)
        local_files = self._scan_local(local_root)

        to_download = []
        to_delete = []
        to_create_dir = []

        for rel_path, r_info in remote_files.items():
            if r_info['type'] == 'dir':
                if rel_path not in local_files: to_create_dir.append(rel_path)
                continue
            if rel_path not in local_files:
                to_download.append(rel_path)
            else:
                l_info = local_files[rel_path]
                size_match = (l_info['size'] == r_info['size'])
                r_ts = self._parse_ftp_time(r_info['mtime'])
                time_match = abs(r_ts - l_info['mtime']) < 2 if r_ts > 0 else True
                if not size_match or not time_match:
                    to_download.append(rel_path)

        for rel_path in local_files:
            if rel_path not in remote_files: to_delete.append(rel_path)

        total_ops = len(to_delete) + len(to_create_dir) + len(to_download)
        if total_ops == 0:
            report("Everything is up to date.", 100, 100)
            return True
            
        processed = 0

        # Delete & Create Dir
        for rel_path in to_delete:
            processed += 1
            report(f"Deleting {rel_path}...", processed, total_ops, status='success')
            p = os.path.join(local_root, rel_path)
            if os.path.isdir(p): import shutil; shutil.rmtree(p, ignore_errors=True)
            else: 
                try: os.remove(p)
                except: pass

        for rel_path in to_create_dir:
            processed += 1
            report(f"Creating directory {rel_path}...", processed, total_ops, status='success')
            os.makedirs(os.path.join(local_root, rel_path), exist_ok=True)

        # Download (Sequential)
        for rel_path in to_download:
            report(f"Downloading {rel_path}...", processed, total_ops)
            local_path = os.path.join(local_root, rel_path)
            remote_abs_path = f"{remote_root}/{rel_path}".replace("//", "/")
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            file_size = remote_files[rel_path]['size']
            success = False
            for attempt in range(self.max_retries):
                try:
                    self._download_file_atomic(remote_abs_path, local_path, file_size, report, processed, total_ops, rel_path)
                    success = True
                    break
                except (socket.error, ftplib.all_errors):
                    try: self._establish_connection()
                    except: pass
            
            processed += 1
            if success:
                r_ts = self._parse_ftp_time(remote_files[rel_path]['mtime'])
                if r_ts > 0: os.utime(local_path, (r_ts, r_ts))
                report(f"Downloaded {rel_path}", processed, total_ops, file_size, file_size, status='success')
            else:
                report(f"Failed {rel_path}", processed, total_ops, status='fail')

        report("Sync completed.", total_ops, total_ops)
        return True

    def _download_file_atomic(self, remote_path, local_path, file_size, report_func, processed_cnt, total_ops, display_name):
        temp_path = local_path + ".tmp"
        bytes_downloaded = 0
        
        # [스마트 버퍼링 재적용]
        if file_size > 10 * 1024 * 1024:   # 10MB 이상
            block_size = 256 * 1024        # 256KB
        elif file_size > 1 * 1024 * 1024:  # 1MB 이상
            block_size = 64 * 1024         # 64KB
        else:                              # 1MB 미만
            block_size = 32 * 1024         # 32KB

        def file_callback(data):
            nonlocal bytes_downloaded
            f.write(data)
            bytes_downloaded += len(data)
            report_func(f"Downloading {display_name}...", processed_cnt, total_ops, bytes_downloaded, file_size)

        with open(temp_path, 'wb') as f:
            self.ftp.retrbinary(f"RETR {remote_path}", file_callback, blocksize=block_size)
        
        if os.path.exists(local_path): os.remove(local_path)
        os.rename(temp_path, local_path)

    def _scan_local(self, local_root):
        local_map = {}
        for root, dirs, files in os.walk(local_root):
            for d in dirs:
                rel = os.path.relpath(os.path.join(root, d), local_root).replace(os.sep, "/")
                local_map[rel] = {'type': 'dir', 'size': 0}
            for f in files:
                abs_p = os.path.join(root, f)
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