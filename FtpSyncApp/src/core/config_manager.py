
import json
import os
import base64

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.default_config = {
            "host": "",
            "port": "21",
            "user": "",
            "password_enc": "", # Simple encoding (Not secure encryption)
            "local_path": os.path.join(os.path.expanduser("~"), "Downloads", "FtpSync")
        }

    def load_config(self):
        if not os.path.exists(self.config_file):
            return self.default_config
        
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**self.default_config, **data} # Merge with defaults
        except Exception:
            return self.default_config

    def save_config(self, host, port, user, password, local_path):
        # Password Encoding (Base64) - 최소한의 가림 처리
        pwd_enc = base64.b64encode(password.encode()).decode() if password else ""
        
        data = {
            "host": host,
            "port": port,
            "user": user,
            "password_enc": pwd_enc,
            "local_path": local_path
        }
        
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def decode_password(self, enc_password):
        try:
            return base64.b64decode(enc_password).decode()
        except:
            return ""
