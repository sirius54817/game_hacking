from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os

class EncryptionUtils:
    @staticmethod
    def generate_key(password: str, salt: bytes = None) -> bytes:
        """Generate an encryption key from a password"""
        if salt is None:
            salt = os.urandom(16)
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt

    @staticmethod
    def encrypt_file(file_path: str, key: bytes) -> tuple:
        """Encrypt a file using the provided key"""
        f = Fernet(key)
        
        with open(file_path, 'rb') as file:
            file_data = file.read()
            
        encrypted_data = f.encrypt(file_data)
        return encrypted_data

    @staticmethod
    def decrypt_file(encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt file data using the provided key"""
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data)
        return decrypted_data 