import hashlib
import os

class UserManager:
    def __init__(self, users_db_path: str):
        self.users_db_path = users_db_path
        self.users = {}
        self.load_users()

    def load_users(self):
        if os.path.exists(self.users_db_path):
            # In a real application, this would be a proper database
            # For demonstration, we're using a simple file
            pass

    def create_user(self, username: str, password: str) -> dict:
        """Create a new user with hashed password"""
        salt = os.urandom(16)
        password_hash = self._hash_password(password, salt)
        
        user = {
            'username': username,
            'password_hash': password_hash,
            'salt': salt,
            'user_id': os.urandom(16).hex()
        }
        
        self.users[username] = user
        return user

    def verify_user(self, username: str, password: str) -> bool:
        """Verify user credentials"""
        if username not in self.users:
            return False
            
        user = self.users[username]
        password_hash = self._hash_password(password, user['salt'])
        return password_hash == user['password_hash']

    @staticmethod
    def _hash_password(password: str, salt: bytes) -> bytes:
        """Hash password with salt using SHA-256"""
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            100000
        ) 