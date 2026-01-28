import os
import time
import ftplib
import socket
import logging
import queue
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

class FtpClientMulti:
    def __init__(self):
        self.host = None
        self.port = 21
        self.user = None
        self.password = None
        self.encoding = 'utf-8'
        self.logger = logging.getLogger(__name__)
        self.max_retries = 3
        self.retry_delay = 2
        self.max_workers = 4 
        self.connection_pool = queue.Queue()
        self.slot_queue = queue.Queue()
        for i in range(self.max_workers):
            self.slot_queue.put(i)

    def _parse_ftp_time(self, ftp_time_str):
        if not ftp_time_str: return 0
        try:
            dt = datetime.strptime(ftp_time_str[:14], "%Y%m%d%H%M%S")
            return dt.replace(tzinfo=timezone.utc).timestamp()
        except Exception: return 0

    def connect(self, host, port, user, password):
        self.host = host; self.port = int(port); self.user = user; self.password = password
        ftp = self._create_new_connection(); ftp.quit()
        self.connection_pool = queue.Queue()

    def _create_new_connection(self):
        for attempt in range(self.max_retries):
            try:
                ftp = ftplib.FTP(); ftp.connect(self.host, self.port, timeout=30)
                ftp.login(self.user, self.password); ftp.encoding = self.encoding
                return ftp
            except: time.sleep(self.retry_delay)
        raise ConnectionError("FTP Connection Failed")

    def _get_worker_connection(self):
        try: return self.connection_pool.get_nowait()
        except queue.Empty: return self._create_new_connection()

    def _return_worker_connection(self, ftp):
        try: ftp.voidcmd("NOOP"); self.connection_pool.put(ftp)
        except: 
            try: ftp.close()
            except: pass

    def list_files_recursive(self, remote_dir):
        ftp = self._get_worker_connection(); file_map = {}
        try: self._walk_ftp(ftp, remote_dir, "", file_map)
        finally: self._return_worker_connection(ftp)
        return file_map

    def _walk_ftp(self, ftp, current_abs_path, relative_prefix, file_map):
        ftp.cwd(current_abs_path); items = list(ftp.mlsd())
        for name, facts in items:
            if name in ('.', '..'): continue
            rel_path = os.path.join(relative_prefix, name).replace(os.sep, "/")
            if facts['type'] == 'dir':
                file_map[rel_path] = {'type': 'dir', 'size': 0}
                self._walk_ftp(ftp, f"{current_abs_path}/{name}", rel_path, file_map)
            else:
                file_map[rel_path] = {'type': 'file', 'size': int(facts.get('size', 0)), 'mtime': facts.get('modify', '')}

    def sync_local_to_remote_mirror(self, remote_root, local_root, callback=None):
        def report(msg, t_curr, t_max, f_curr=0, f_max=0, status=None, slot_idx=-1):
            if callback: callback(msg, t_curr, t_max, f_curr, f_max, status, slot_idx)

        report("Analyzing files...", 0, 100)
        try: remote_files = self.list_files_recursive(remote_root)
        except Exception as e: report(f"Fatal: {e}", 0, 0, status='fail'); return False

        local_files = self._scan_local(local_root)
        to_download = []; to_delete = []; to_create_dir = []

        for rel_path, r_info in remote_files.items():
            if r_info['type'] == 'dir':
                if rel_path not in local_files: to_create_dir.append(rel_path)
                continue
            if rel_path not in local_files: to_download.append(rel_path)
            else:
                l_info = local_files[rel_path]
                size_match = (l_info['size'] == r_info['size'])
                r_ts = self._parse_ftp_time(r_info['mtime'])
                time_match = abs(r_ts - l_info['mtime']) < 2 if r_ts > 0 else True
                if not size_match or not time_match: to_download.append(rel_path)

        for rel_path in local_files:
            if rel_path not in remote_files: to_delete.append(rel_path)

        # [변경] 전체 용량 계산
        total_bytes = sum(remote_files[p]['size'] for p in to_download)
        total_ops = len(to_delete) + len(to_create_dir) + len(to_download)
        report("Plan", 0, total_ops, 0, total_bytes, status='plan')

        if total_ops == 0:
            report("Everything is up to date.", 100, 100)
            return True
            
        processed = 0
        for rel_path in to_delete:
            processed += 1; report(f"Deleting {rel_path}...", processed, total_ops, status='success')
            p = os.path.join(local_root, rel_path)
            if os.path.isdir(p): import shutil; shutil.rmtree(p, ignore_errors=True)
            else: 
                try: os.remove(p); pass
                except: pass

        for rel_path in to_create_dir:
            processed += 1; report(f"Creating directory {rel_path}...", processed, total_ops, status='success')
            os.makedirs(os.path.join(local_root, rel_path), exist_ok=True)

        if to_download:
            report(f"Starting concurrent download ({len(to_download)} files)...", processed, total_ops)
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {}
                for rel_path in to_download:
                    remote_abs_path = f"{remote_root}/{rel_path}".replace("//", "/")
                    f_size = remote_files[rel_path]['size']; r_m = remote_files[rel_path]['mtime']
                    future = executor.submit(self._download_task, rel_path, remote_abs_path, local_root, f_size, r_m, report, total_ops)
                    futures[future] = rel_path
                for future in as_completed(futures):
                    processed += 1; report(f"Processed {futures[future]}", processed, total_ops)
                    try:
                        success = future.result()
                        if not success: report(f"Failed {futures[future]}", processed, total_ops, status='fail')
                    except: report(f"Error {futures[future]}", processed, total_ops, status='fail')
                         
        report("Sync completed.", total_ops, total_ops)
        return True

    def _download_task(self, rel_path, remote_path, local_root, file_size, r_mtime, report_func, total_ops):
        slot_idx = self.slot_queue.get()
        local_path = os.path.join(local_root, rel_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        ftp = self._get_worker_connection()
        try:
            if file_size > 10 * 1024 * 1024: b_size = 256 * 1024
            elif file_size > 1 * 1024 * 1024: b_size = 64 * 1024
            else: b_size = 32 * 1024
            temp_path = local_path + ".tmp"; b_down = 0; last_pct = -1
            def file_callback(data):
                nonlocal b_down, last_pct; f.write(data); b_down += len(data)
                if file_size > 0:
                    curr_pct = int((b_down / file_size) * 100)
                    if curr_pct != last_pct:
                        report_func(f"Downloading {rel_path}...", 0, total_ops, b_down, file_size, slot_idx=slot_idx)
                        last_pct = curr_pct
            with open(temp_path, 'wb') as f: ftp.retrbinary(f"RETR {remote_path}", file_callback, blocksize=b_size)
            if os.path.exists(local_path): os.remove(local_path)
            os.rename(temp_path, local_path)
            r_ts = self._parse_ftp_time(r_mtime)
            if r_ts > 0: os.utime(local_path, (r_ts, r_ts))
            report_func(f"Downloaded {rel_path}", 0, total_ops, file_size, file_size, status='success', slot_idx=slot_idx)
            return True
        except: return False
        finally: self._return_worker_connection(ftp); self.slot_queue.put(slot_idx)

    def _scan_local(self, local_root):
        local_map = {}
        for root, dirs, files in os.walk(local_root):
            for d in dirs:
                rel = os.path.relpath(os.path.join(root, d), local_root).replace(os.sep, "/")
                local_map[rel] = {'type': 'dir', 'size': 0}
            for f in files:
                abs_p = os.path.join(root, f); rel = os.path.relpath(abs_p, local_root).replace(os.sep, "/")
                local_map[rel] = {'type': 'file', 'size': os.path.getsize(abs_p), 'mtime': os.path.getmtime(abs_p)}
        return local_map

    def close(self):
        while not self.connection_pool.empty():
            try: self.connection_pool.get().quit()
            except: pass