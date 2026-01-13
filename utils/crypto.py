"""Cryptography utilities for secure communication"""

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2


class CryptoHandler:
    """Handles encryption and decryption for C2 communications"""
    
    def __init__(self, password=None):
        if password is None:
            password = "default-c2-password"
        
        # Generate key from password
        salt = b'c2_salt_value_12345'  # In production, use random salt per agent
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.cipher = Fernet(key)
    
    def encrypt(self, data):
        """Encrypt data"""
        if isinstance(data, str):
            data = data.encode()
        return base64.b64encode(self.cipher.encrypt(data)).decode()
    
    def decrypt(self, encrypted_data):
        """Decrypt data"""
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        decrypted = self.cipher.decrypt(base64.b64decode(encrypted_data))
        return decrypted.decode()
    
    @staticmethod
    def generate_agent_id():
        """Generate unique agent ID"""
        return base64.b64encode(os.urandom(16)).decode()[:22]
