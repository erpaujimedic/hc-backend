import os
from cryptography.fernet import Fernet

class DataSecurityManager:
    """
    Silicon Valley Standard: Cryptographic shield for sensitive healthcare data.
    Implements AES-based symmetric encryption to protect Patient/Nurse PII.
    """
    
    # PERUBAHAN CRITICAL:
    # Wajib ambil dari environment. Kalau nggak ada, aplikasi langsung crash
    # Ini mencegah aplikasi jalan dengan key baru dan membuat data lama tidak bisa di-dekripsi.
    _raw_key = os.getenv("FIELD_ENCRYPTION_KEY")
    if not _raw_key:
        raise ValueError("CRITICAL FAILURE: 'FIELD_ENCRYPTION_KEY' is missing from environment variables. Halting application to prevent permanent data corruption.")
    
    _ENCRYPTION_KEY: bytes = _raw_key.encode()
    _fernet = Fernet(_ENCRYPTION_KEY)

    @classmethod
    def encrypt_sensitive_data(cls, plain_text: str) -> str:
        """
        Encrypts sensitive text fields (e.g., patient clinical notes, medical records, identity numbers)
        before persisting them into the database layer.
        """
        if not plain_text:
            return plain_text
        try:
            encrypted_bytes = cls._fernet.encrypt(plain_text.encode('utf-8'))
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Cryptographic encryption failure: {str(e)}")

    @classmethod
    def decrypt_sensitive_data(cls, encrypted_text: str) -> str:
        """
        Decrypts securely encrypted data retrieved from the database 
        into readable plain text for the authenticated user interface.
        """
        if not encrypted_text:
            return encrypted_text
        try:
            decrypted_bytes = cls._fernet.decrypt(encrypted_text.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Cryptographic decryption failure: {str(e)}")