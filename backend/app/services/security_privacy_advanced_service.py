from typing import Dict, List, Optional
import json
import os
import uuid
import hashlib
from datetime import datetime
from app.core.config import settings
try:
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    Fernet = None


class SecurityPrivacyAdvancedService:
    def __init__(self):
        self.security_file = os.path.join(settings.STORAGE_PATH, "security_settings.json")
        self.two_factor_file = os.path.join(settings.STORAGE_PATH, "two_factor_auth.json")
        self.privacy_file = os.path.join(settings.STORAGE_PATH, "privacy_settings.json")
        self.security_logs_file = os.path.join(settings.STORAGE_PATH, "security_logs.json")
        self._ensure_files()
        self._load_encryption_key()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        for file_path in [self.security_file, self.two_factor_file, self.privacy_file, self.security_logs_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
    
    def _load_encryption_key(self):
        """Şifreleme anahtarını yükler veya oluşturur."""
        if not CRYPTOGRAPHY_AVAILABLE:
            self.encryption_key = None
            self.cipher_suite = None
            return
        
        key_file = os.path.join(settings.STORAGE_PATH, ".encryption_key")
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                self.encryption_key = f.read()
        else:
            self.encryption_key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(self.encryption_key)
        
        self.cipher_suite = Fernet(self.encryption_key)
    
    def enable_two_factor_auth(self, user_id: str) -> Dict:
        """İki faktörlü kimlik doğrulamayı etkinleştirir."""
        secret = str(uuid.uuid4()).replace('-', '')[:16]  # Basit secret (gerçek uygulamada daha güvenli olmalı)
        
        with open(self.two_factor_file, 'r', encoding='utf-8') as f:
            two_factor = json.load(f)
        
        two_factor[user_id] = {
            "enabled": True,
            "secret": secret,
            "backup_codes": [str(uuid.uuid4())[:8] for _ in range(5)],
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.two_factor_file, 'w', encoding='utf-8') as f:
            json.dump(two_factor, f, ensure_ascii=False, indent=2)
        
        return {
            "user_id": user_id,
            "enabled": True,
            "secret": secret,
            "backup_codes": two_factor[user_id]["backup_codes"]
        }
    
    def verify_two_factor_code(self, user_id: str, code: str) -> bool:
        """İki faktörlü kod doğrular."""
        with open(self.two_factor_file, 'r', encoding='utf-8') as f:
            two_factor = json.load(f)
        
        user_2fa = two_factor.get(user_id)
        if not user_2fa or not user_2fa.get('enabled'):
            return False
        
        # Basit doğrulama (gerçek uygulamada TOTP kullanılmalı)
        return code in user_2fa.get('backup_codes', [])
    
    def set_privacy_settings(
        self,
        user_id: str,
        settings: Dict
    ) -> Dict:
        """Gizlilik ayarlarını kaydeder."""
        with open(self.privacy_file, 'r', encoding='utf-8') as f:
            privacy = json.load(f)
        
        privacy[user_id] = {
            **settings,
            "updated_at": datetime.now().isoformat()
        }
        
        with open(self.privacy_file, 'w', encoding='utf-8') as f:
            json.dump(privacy, f, ensure_ascii=False, indent=2)
        
        return privacy[user_id]
    
    def get_privacy_settings(self, user_id: str) -> Dict:
        """Gizlilik ayarlarını getirir."""
        with open(self.privacy_file, 'r', encoding='utf-8') as f:
            privacy = json.load(f)
        return privacy.get(user_id, {
            "profile_visibility": "public",
            "story_visibility": "public",
            "data_sharing": False
        })
    
    def encrypt_data(self, data: str) -> str:
        """Veriyi şifreler."""
        if not CRYPTOGRAPHY_AVAILABLE or self.cipher_suite is None:
            # Basit encoding (gerçek uygulamada cryptography gerekli)
            import base64
            return base64.b64encode(data.encode()).decode()
        encrypted = self.cipher_suite.encrypt(data.encode())
        return encrypted.decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Şifreli veriyi çözer."""
        if not CRYPTOGRAPHY_AVAILABLE or self.cipher_suite is None:
            # Basit decoding (gerçek uygulamada cryptography gerekli)
            import base64
            return base64.b64decode(encrypted_data.encode()).decode()
        decrypted = self.cipher_suite.decrypt(encrypted_data.encode())
        return decrypted.decode()
    
    def log_security_event(
        self,
        user_id: str,
        event_type: str,
        details: Dict
    ):
        """Güvenlik olayını loglar."""
        log_entry = {
            "log_id": str(uuid.uuid4()),
            "user_id": user_id,
            "event_type": event_type,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "ip_address": details.get('ip_address', 'unknown')
        }
        
        with open(self.security_logs_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        logs.append(log_entry)
        
        # Son 1000 log'u tut
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        with open(self.security_logs_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    
    def get_security_logs(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Güvenlik loglarını getirir."""
        with open(self.security_logs_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        user_logs = [l for l in logs if l.get('user_id') == user_id]
        return user_logs[-limit:]

