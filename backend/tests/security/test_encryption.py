"""Tests for encryption service.

This module tests the encryption and decryption functionality
to ensure data security and proper key management.
"""

import pytest

from src.security.encryption import (
    DecryptionError,
    EncryptionError,
    EncryptionService,
    decrypt_data,
    derive_encryption_key,
    encrypt_data,
    generate_user_salt,
    hash_encryption_key,
    rotate_encryption_key,
    setup_user_encryption,
    verify_and_get_encryption_key,
)


class TestEncryptionBasics:
    """Test basic encryption operations."""

    def test_generate_user_salt(self) -> None:
        """Test that user salt generation creates unique salts."""
        salt1 = generate_user_salt()
        salt2 = generate_user_salt()

        assert salt1 != salt2
        assert len(salt1) > 0
        assert len(salt2) > 0

    def test_derive_encryption_key(self) -> None:
        """Test key derivation from password and salt."""
        password = "test_password_123"
        salt = generate_user_salt()

        key1 = derive_encryption_key(password, salt)
        key2 = derive_encryption_key(password, salt)

        # Same password and salt should produce same key
        assert key1 == key2

        # Different password should produce different key
        key3 = derive_encryption_key("different_password", salt)
        assert key1 != key3

        # Different salt should produce different key
        different_salt = generate_user_salt()
        key4 = derive_encryption_key(password, different_salt)
        assert key1 != key4

    def test_hash_encryption_key(self) -> None:
        """Test encryption key hashing."""
        password = "test_password_123"
        salt = generate_user_salt()
        key = derive_encryption_key(password, salt)

        hash1 = hash_encryption_key(key)
        hash2 = hash_encryption_key(key)

        # Same key should produce same hash
        assert hash1 == hash2

        # Hash should be hex string
        assert len(hash1) == 64  # SHA256 hex digest
        assert all(c in "0123456789abcdef" for c in hash1)


class TestEncryptionDecryption:
    """Test encryption and decryption operations."""

    def test_encrypt_decrypt_simple(self) -> None:
        """Test basic encryption and decryption."""
        password = "my_secure_password"
        salt = generate_user_salt()
        key = derive_encryption_key(password, salt)

        original_data = "This is sensitive journal data"
        encrypted = encrypt_data(original_data, key)
        decrypted = decrypt_data(encrypted, key)

        assert decrypted == original_data
        assert encrypted != original_data

    def test_encrypt_empty_string(self) -> None:
        """Test encryption of empty string."""
        password = "password123"
        salt = generate_user_salt()
        key = derive_encryption_key(password, salt)

        encrypted = encrypt_data("", key)
        decrypted = decrypt_data(encrypted, key)

        assert decrypted == ""
        assert encrypted == ""

    def test_encrypt_unicode(self) -> None:
        """Test encryption of unicode characters."""
        password = "password123"
        salt = generate_user_salt()
        key = derive_encryption_key(password, salt)

        original_data = "Hello 世界 🌍 Привет"
        encrypted = encrypt_data(original_data, key)
        decrypted = decrypt_data(encrypted, key)

        assert decrypted == original_data

    def test_encrypt_long_text(self) -> None:
        """Test encryption of long text."""
        password = "password123"
        salt = generate_user_salt()
        key = derive_encryption_key(password, salt)

        original_data = "A" * 10000  # 10KB of text
        encrypted = encrypt_data(original_data, key)
        decrypted = decrypt_data(encrypted, key)

        assert decrypted == original_data

    def test_decrypt_wrong_key(self) -> None:
        """Test that decryption fails with wrong key."""
        password = "password123"
        salt = generate_user_salt()
        key = derive_encryption_key(password, salt)

        original_data = "Sensitive data"
        encrypted = encrypt_data(original_data, key)

        # Try to decrypt with different key
        wrong_key = derive_encryption_key("wrong_password", salt)

        with pytest.raises(DecryptionError):
            decrypt_data(encrypted, wrong_key)

    def test_decrypt_corrupted_data(self) -> None:
        """Test that decryption fails with corrupted data."""
        password = "password123"
        salt = generate_user_salt()
        key = derive_encryption_key(password, salt)

        corrupted_data = "invalid_encrypted_data"

        with pytest.raises(DecryptionError):
            decrypt_data(corrupted_data, key)


class TestEncryptionService:
    """Test EncryptionService class."""

    def test_encryption_service_init(self) -> None:
        """Test encryption service initialization."""
        password = "test_password"
        salt = generate_user_salt()

        service = EncryptionService(password, salt)

        assert service.key_hash is not None
        assert len(service.key_hash) == 64

    def test_encryption_service_encrypt_decrypt(self) -> None:
        """Test encryption service encrypt/decrypt methods."""
        password = "test_password"
        salt = generate_user_salt()
        service = EncryptionService(password, salt)

        original_data = "Sensitive journal entry"
        encrypted = service.encrypt(original_data)
        decrypted = service.decrypt(encrypted)

        assert decrypted == original_data

    def test_encryption_service_verify_key(self) -> None:
        """Test key verification."""
        password = "test_password"
        salt = generate_user_salt()
        service = EncryptionService(password, salt)

        # Should verify with correct hash
        assert service.verify_key(service.key_hash)

        # Should not verify with wrong hash
        wrong_service = EncryptionService("wrong_password", salt)
        assert not service.verify_key(wrong_service.key_hash)


class TestKeyRotation:
    """Test encryption key rotation."""

    def test_rotate_encryption_key(self) -> None:
        """Test key rotation with password change."""
        old_password = "old_password_123"
        new_password = "new_password_456"
        salt = generate_user_salt()

        # Encrypt data with old password
        old_key = derive_encryption_key(old_password, salt)
        original_data = "Important journal entry"
        encrypted_data = encrypt_data(original_data, old_key)

        # Rotate key
        new_encrypted, new_key, new_hash = rotate_encryption_key(
            old_password, new_password, salt, encrypted_data
        )

        # Verify new encryption works
        decrypted = decrypt_data(new_encrypted, new_key)
        assert decrypted == original_data

        # Verify old key no longer works
        with pytest.raises(DecryptionError):
            decrypt_data(new_encrypted, old_key)

    def test_rotate_key_wrong_old_password(self) -> None:
        """Test that rotation fails with wrong old password."""
        old_password = "old_password_123"
        new_password = "new_password_456"
        salt = generate_user_salt()

        # Encrypt data with old password
        old_key = derive_encryption_key(old_password, salt)
        original_data = "Important journal entry"
        encrypted_data = encrypt_data(original_data, old_key)

        # Try to rotate with wrong old password
        with pytest.raises(DecryptionError):
            rotate_encryption_key("wrong_password", new_password, salt, encrypted_data)


class TestSetupAndVerification:
    """Test user encryption setup and verification."""

    def test_setup_user_encryption(self) -> None:
        """Test setting up encryption for a new user."""
        password = "user_password_123"

        salt, key, key_hash = setup_user_encryption(password)

        # Verify components
        assert len(salt) > 0
        assert len(key) > 0
        assert len(key_hash) == 64

        # Verify key can be derived again
        derived_key = derive_encryption_key(password, salt)
        assert derived_key == key

    def test_verify_and_get_encryption_key_correct(self) -> None:
        """Test verification with correct password."""
        password = "user_password_123"
        salt, key, key_hash = setup_user_encryption(password)

        verified_key = verify_and_get_encryption_key(password, salt, key_hash)

        assert verified_key is not None
        assert verified_key == key

    def test_verify_and_get_encryption_key_wrong(self) -> None:
        """Test verification with wrong password."""
        password = "user_password_123"
        salt, key, key_hash = setup_user_encryption(password)

        verified_key = verify_and_get_encryption_key("wrong_password", salt, key_hash)

        assert verified_key is None


class TestSecurityProperties:
    """Test security properties of encryption."""

    def test_same_plaintext_different_ciphertext(self) -> None:
        """Test that same plaintext produces different ciphertext each time.

        This is important for security - encryption should be non-deterministic.
        """
        password = "password123"
        salt = generate_user_salt()
        key = derive_encryption_key(password, salt)

        plaintext = "Same message"
        encrypted1 = encrypt_data(plaintext, key)
        encrypted2 = encrypt_data(plaintext, key)

        # Ciphertext should be different (Fernet includes timestamp and IV)
        assert encrypted1 != encrypted2

        # But both should decrypt to same plaintext
        assert decrypt_data(encrypted1, key) == plaintext
        assert decrypt_data(encrypted2, key) == plaintext

    def test_key_derivation_is_deterministic(self) -> None:
        """Test that key derivation is deterministic."""
        password = "password123"
        salt = generate_user_salt()

        # Derive key multiple times
        key1 = derive_encryption_key(password, salt)
        key2 = derive_encryption_key(password, salt)
        key3 = derive_encryption_key(password, salt)

        # All keys should be identical
        assert key1 == key2 == key3

    def test_encryption_preserves_data_integrity(self) -> None:
        """Test that encryption/decryption preserves data integrity."""
        password = "password123"
        salt = generate_user_salt()
        key = derive_encryption_key(password, salt)

        # Test various data types and edge cases
        test_cases = [
            "Simple text",
            "Text with\nnewlines\nand\ttabs",
            "Special chars: !@#$%^&*()_+-=[]{}|;:',.<>?/",
            "Unicode: 日本語 한글 العربية",
            "Emoji: 😀😃😄😁🎉🎊",
            "Mixed: Hello 世界! 😊",
            "Long: " + "x" * 1000,
            "",  # Empty string
        ]

        for original in test_cases:
            encrypted = encrypt_data(original, key)
            decrypted = decrypt_data(encrypted, key)
            assert decrypted == original, f"Failed for: {original[:50]}"
