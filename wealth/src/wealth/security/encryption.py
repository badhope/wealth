"""Encryption and security utilities for data protection."""

import base64
import hashlib
import os
from typing import Optional, Any
from dataclasses import dataclass
from loguru import logger

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False
    logger.warning("cryptography not available, using basic encoding")


@dataclass
class EncryptionConfig:
    algorithm: str = "AES-256"
    key_derivation_iterations: int = 100000
    salt_length: int = 32


class DataEncryptor:
    def __init__(self, master_key: Optional[str] = None, config: EncryptionConfig = None):
        self.config = config or EncryptionConfig()
        self._fernet: Optional[Fernet] = None

        if HAS_CRYPTO:
            if master_key:
                self._setup_encryption(master_key)
        else:
            self._key = master_key.encode() if master_key else b"default_key_change_this"

    def _setup_encryption(self, master_key: str):
        if not HAS_CRYPTO:
            return

        salt = b"wealth_platform_salt"
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.config.key_derivation_iterations,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        self._fernet = Fernet(key)

    def encrypt(self, data: str) -> str:
        if HAS_CRYPTO and self._fernet:
            encrypted = self._fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        else:
            encoded = base64.b64encode(data.encode()).decode()
            return encoded

    def decrypt(self, encrypted_data: str) -> str:
        if HAS_CRYPTO and self._fernet:
            try:
                decoded = base64.urlsafe_b64decode(encrypted_data.encode())
                decrypted = self._fernet.decrypt(decoded)
                return decrypted.decode()
            except Exception as e:
                logger.error(f"Decryption failed: {e}")
                return ""
        else:
            try:
                return base64.b64decode(encrypted_data.encode()).decode()
            except Exception:
                return ""

    def encrypt_file(self, input_path: str, output_path: str):
        with open(input_path, 'rb') as f:
            data = f.read()
        encrypted = self.encrypt(base64.b64encode(data).decode())
        with open(output_path, 'w') as f:
            f.write(encrypted)

    def decrypt_file(self, input_path: str, output_path: str):
        with open(input_path, 'r') as f:
            encrypted = f.read()
        decrypted = base64.b64decode(self.decrypt(encrypted))
        with open(output_path, 'wb') as f:
            f.write(decrypted)


class Role:
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    ANALYST = "analyst"


class Permission:
    READ_STOCKS = "read_stocks"
    WRITE_STOCKS = "write_stocks"
    READ_ALERTS = "read_alerts"
    WRITE_ALERTS = "write_alerts"
    READ_BACKTEST = "read_backtest"
    WRITE_BACKTEST = "write_backtest"
    READ_PORTFOLIO = "read_portfolio"
    WRITE_PORTFOLIO = "write_portfolio"
    ADMIN_SETTINGS = "admin_settings"


ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.READ_STOCKS, Permission.WRITE_STOCKS,
        Permission.READ_ALERTS, Permission.WRITE_ALERTS,
        Permission.READ_BACKTEST, Permission.WRITE_BACKTEST,
        Permission.READ_PORTFOLIO, Permission.WRITE_PORTFOLIO,
        Permission.ADMIN_SETTINGS,
    ],
    Role.ANALYST: [
        Permission.READ_STOCKS, Permission.READ_ALERTS, Permission.READ_BACKTEST,
        Permission.READ_PORTFOLIO,
    ],
    Role.USER: [
        Permission.READ_STOCKS, Permission.READ_ALERTS,
        Permission.READ_PORTFOLIO,
    ],
    Role.GUEST: [
        Permission.READ_STOCKS,
    ],
}


@dataclass
class User:
    username: str
    role: str
    encrypted_password: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True


class AccessControl:
    def __init__(self):
        self.users: dict[str, User] = {}
        self._encryptor = DataEncryptor()

    def add_user(self, username: str, password: str, role: str = Role.USER, email: Optional[str] = None) -> bool:
        if username in self.users:
            logger.warning(f"User {username} already exists")
            return False

        encrypted_pwd = self._encryptor.encrypt(password)

        self.users[username] = User(
            username=username,
            role=role,
            encrypted_password=encrypted_pwd,
            email=email
        )
        logger.info(f"User {username} added with role {role}")
        return True

    def authenticate(self, username: str, password: str) -> bool:
        if username not in self.users:
            return False

        user = self.users[username]
        if not user.is_active:
            return False

        decrypted_pwd = self._encryptor.decrypt(user.encrypted_password)
        return decrypted_pwd == password

    def check_permission(self, username: str, permission: Permission) -> bool:
        if username not in self.users:
            return False

        user = self.users[username]
        if not user.is_active:
            return False

        return permission in ROLE_PERMISSIONS.get(user.role, [])

    def get_user_role(self, username: str) -> Optional[str]:
        if username not in self.users:
            return None
        return self.users[username].role

    def update_user_role(self, username: str, new_role: str) -> bool:
        if username not in self.users:
            return False

        self.users[username].role = new_role
        logger.info(f"User {username} role updated to {new_role}")
        return True

    def deactivate_user(self, username: str) -> bool:
        if username not in self.users:
            return False

        self.users[username].is_active = False
        logger.info(f"User {username} deactivated")
        return True

    def activate_user(self, username: str) -> bool:
        if username not in self.users:
            return False

        self.users[username].is_active = True
        logger.info(f"User {username} activated")
        return True


access_control = AccessControl()
