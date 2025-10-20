"""Encryption service for end-to-end encryption of sensitive data.

This module provides encryption/decryption utilities using Fernet symmetric encryption
with key derivation from user password and server salt.

Security features:
- Fernet symmetric encryption (AES-128 in CBC mode with HMAC for authentication)
- PBKDF2-HMAC-SHA256 for key derivation from passwords
- Per-user salt for key derivation
- Server-side master salt for additional security
- Automatic key rotation support
"""

import base64
import hashlib
import secrets
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

# Server-side master salt - should be loaded from environment in production
# This provides an additional layer of security beyond user passwords
MASTER_SALT = b"kai_wellness_platform_master_salt_v1"  # Should be in .env in production

# PBKDF2 iterations for key derivation (OWASP recommends 600,000+ for PBKDF2-HMAC-SHA256)
PBKDF2_ITERATIONS = 600_000


class EncryptionError(Exception):
    """Base exception for encryption-related errors."""

    pass


class DecryptionError(Exception):
    """Exception raised when decryption fails."""

    pass


def generate_user_salt() -> str:
    """Generate a random salt for user-specific key derivation.

    Returns:
        Base64-encoded salt string suitable for database storage.
    """
    salt = secrets.token_bytes(32)  # 256-bit salt
    return base64.b64encode(salt).decode("utf-8")


def derive_encryption_key(password: str, user_salt: str) -> bytes:
    """Derive an encryption key from user password and salt.

    Uses PBKDF2-HMAC-SHA256 with high iteration count for secure key derivation.
    The derived key is suitable for use with Fernet encryption.

    Args:
        password: User's password (plain text)
        user_salt: Base64-encoded user-specific salt

    Returns:
        32-byte key suitable for Fernet encryption

    Raises:
        EncryptionError: If key derivation fails
    """
    try:
        # Decode user salt
        salt_bytes = base64.b64decode(user_salt.encode("utf-8"))

        # Combine user salt with master salt for additional security
        combined_salt = salt_bytes + MASTER_SALT

        # Derive key using PBKDF2
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=combined_salt,
            iterations=PBKDF2_ITERATIONS,
        )

        key = kdf.derive(password.encode("utf-8"))
        return base64.urlsafe_b64encode(key)

    except Exception as e:
        raise EncryptionError(f"Failed to derive encryption key: {e!s}") from e


def hash_encryption_key(encryption_key: bytes) -> str:
    """Create a hash of the encryption key for verification purposes.

    This hash is stored in the database to verify that the correct password
    is being used for decryption without storing the actual key.

    Args:
        encryption_key: The derived encryption key

    Returns:
        Hex-encoded SHA256 hash of the key
    """
    return hashlib.sha256(encryption_key).hexdigest()


def encrypt_data(data: str, encryption_key: bytes) -> str:
    """Encrypt data using Fernet symmetric encryption.

    Args:
        data: Plain text data to encrypt
        encryption_key: Encryption key (from derive_encryption_key)

    Returns:
        Base64-encoded encrypted data (Fernet token)

    Raises:
        EncryptionError: If encryption fails
    """
    try:
        if not data:
            return ""

        fernet = Fernet(encryption_key)
        encrypted_bytes = fernet.encrypt(data.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")

    except Exception as e:
        raise EncryptionError(f"Failed to encrypt data: {e!s}") from e


def decrypt_data(encrypted_data: str, encryption_key: bytes) -> str:
    """Decrypt data using Fernet symmetric encryption.

    Args:
        encrypted_data: Base64-encoded encrypted data (Fernet token)
        encryption_key: Encryption key (from derive_encryption_key)

    Returns:
        Decrypted plain text data

    Raises:
        DecryptionError: If decryption fails (wrong key, corrupted data, etc.)
    """
    try:
        if not encrypted_data:
            return ""

        fernet = Fernet(encryption_key)
        decrypted_bytes = fernet.decrypt(encrypted_data.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")

    except InvalidToken as e:
        raise DecryptionError(
            "Failed to decrypt data: invalid token or wrong encryption key"
        ) from e
    except Exception as e:
        raise DecryptionError(f"Failed to decrypt data: {e!s}") from e


def rotate_encryption_key(
    old_password: str, new_password: str, user_salt: str, encrypted_data: str
) -> tuple[str, bytes, str]:
    """Rotate encryption key by re-encrypting data with new password.

    This is used when a user changes their password. The data is decrypted
    with the old key and re-encrypted with the new key.

    Args:
        old_password: User's old password
        new_password: User's new password
        user_salt: User's salt (remains the same)
        encrypted_data: Currently encrypted data

    Returns:
        Tuple of (re-encrypted_data, new_encryption_key, new_key_hash)

    Raises:
        DecryptionError: If data cannot be decrypted with old password
        EncryptionError: If data cannot be encrypted with new password
    """
    # Derive old key and decrypt
    old_key = derive_encryption_key(old_password, user_salt)
    decrypted_data = decrypt_data(encrypted_data, old_key)

    # Derive new key and encrypt
    new_key = derive_encryption_key(new_password, user_salt)
    new_encrypted_data = encrypt_data(decrypted_data, new_key)
    new_key_hash = hash_encryption_key(new_key)

    return new_encrypted_data, new_key, new_key_hash


class EncryptionService:
    """Service class for managing encryption operations.

    This class provides a convenient interface for encryption operations
    and maintains the encryption key in memory for the duration of a session.
    """

    def __init__(self, password: str, user_salt: str):
        """Initialize encryption service with user credentials.

        Args:
            password: User's password
            user_salt: User-specific salt
        """
        self._encryption_key = derive_encryption_key(password, user_salt)
        self._key_hash = hash_encryption_key(self._encryption_key)

    @property
    def key_hash(self) -> str:
        """Get the hash of the current encryption key."""
        return self._key_hash

    def encrypt(self, data: str) -> str:
        """Encrypt data using the initialized encryption key.

        Args:
            data: Plain text data to encrypt

        Returns:
            Encrypted data
        """
        return encrypt_data(data, self._encryption_key)

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data using the initialized encryption key.

        Args:
            encrypted_data: Encrypted data

        Returns:
            Decrypted plain text data
        """
        return decrypt_data(encrypted_data, self._encryption_key)

    def verify_key(self, stored_key_hash: str) -> bool:
        """Verify that the current key matches the stored key hash.

        Args:
            stored_key_hash: Hash of the encryption key stored in database

        Returns:
            True if keys match, False otherwise
        """
        return self._key_hash == stored_key_hash

    def rotate_key(self, new_password: str, user_salt: str) -> tuple[bytes, str]:
        """Generate a new encryption key from a new password.

        Args:
            new_password: New user password
            user_salt: User salt (remains the same)

        Returns:
            Tuple of (new_encryption_key, new_key_hash)
        """
        new_key = derive_encryption_key(new_password, user_salt)
        new_key_hash = hash_encryption_key(new_key)
        return new_key, new_key_hash


# Convenience functions for common operations


def setup_user_encryption(password: str) -> tuple[str, bytes, str]:
    """Set up encryption for a new user.

    Generates a salt, derives an encryption key, and creates a key hash.

    Args:
        password: User's password

    Returns:
        Tuple of (user_salt, encryption_key, key_hash)
    """
    user_salt = generate_user_salt()
    encryption_key = derive_encryption_key(password, user_salt)
    key_hash = hash_encryption_key(encryption_key)
    return user_salt, encryption_key, key_hash


def verify_and_get_encryption_key(
    password: str, user_salt: str, stored_key_hash: str
) -> Optional[bytes]:
    """Verify password and return encryption key if correct.

    Args:
        password: User's password
        user_salt: User's salt from database
        stored_key_hash: Stored key hash from database

    Returns:
        Encryption key if password is correct, None otherwise
    """
    try:
        encryption_key = derive_encryption_key(password, user_salt)
        key_hash = hash_encryption_key(encryption_key)

        if key_hash == stored_key_hash:
            return encryption_key
        return None

    except Exception:
        return None
