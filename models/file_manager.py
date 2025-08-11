import os
from utils.encryption_utils import EncryptionUtils
from datetime import datetime

class FileManager:
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.encryption_utils = EncryptionUtils()

    def save_encrypted_file(self, file_path: str, password: str, user_id: str) -> dict:
        """
        Encrypt and save a file with associated metadata
        """
        # Generate encryption key from password
        key, salt = self.encryption_utils.generate_key(password)
        
        # Encrypt the file
        encrypted_data = self.encryption_utils.encrypt_file(file_path, key)
        
        # Generate unique filename
        file_id = os.urandom(16).hex()
        encrypted_filename = f"{file_id}.encrypted"
        
        # Save encrypted file
        save_path = os.path.join(self.storage_path, encrypted_filename)
        with open(save_path, 'wb') as f:
            f.write(encrypted_data)
            
        # Create metadata
        metadata = {
            'file_id': file_id,
            'original_filename': os.path.basename(file_path),
            'encrypted_filename': encrypted_filename,
            'owner_id': user_id,
            'salt': salt,
            'created_at': datetime.now().isoformat(),
            'shared_with': []
        }
        
        return metadata

    def decrypt_and_read_file(self, encrypted_filename: str, password: str, salt: bytes) -> bytes:
        """
        Decrypt and read a file's contents
        """
        # Generate key from password and salt
        key, _ = self.encryption_utils.generate_key(password, salt)
        
        # Read encrypted file
        file_path = os.path.join(self.storage_path, encrypted_filename)
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
            
        # Decrypt data
        decrypted_data = self.encryption_utils.decrypt_file(encrypted_data, key)
        return decrypted_data 