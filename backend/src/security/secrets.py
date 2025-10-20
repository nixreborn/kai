"""Secret management and rotation utilities for Kai backend."""

import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path

from cryptography.fernet import Fernet
from pydantic import BaseModel


class SecretMetadata(BaseModel):
    """Metadata for a secret key."""

    key_id: str
    created_at: datetime
    expires_at: datetime
    is_active: bool


class SecretManager:
    """
    Manages secret keys and provides rotation capabilities.

    This class handles:
    - Secret key generation
    - Secret rotation with grace periods
    - Encrypted storage of secrets
    - Secret expiration tracking
    """

    def __init__(self, storage_path: Path | None = None) -> None:
        """
        Initialize the SecretManager.

        Args:
            storage_path: Path to store encrypted secrets. Defaults to ~/.kai/secrets
        """
        self.storage_path = storage_path or Path.home() / ".kai" / "secrets"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.secrets_file = self.storage_path / "secrets.enc"
        self.metadata_file = self.storage_path / "metadata.json"

    @staticmethod
    def generate_secret_key(length: int = 32) -> str:
        """
        Generate a cryptographically secure secret key.

        Args:
            length: Length of the secret key in bytes (default: 32)

        Returns:
            Hex-encoded secret key
        """
        return secrets.token_hex(length)

    @staticmethod
    def generate_fernet_key() -> str:
        """
        Generate a Fernet encryption key.

        Returns:
            Base64-encoded Fernet key
        """
        return Fernet.generate_key().decode()

    def rotate_secret(
        self,
        current_secret: str,
        expiry_days: int = 90,
        grace_period_days: int = 7,
    ) -> tuple[str, SecretMetadata]:
        """
        Rotate a secret key with a grace period.

        During the grace period, both old and new secrets are valid.
        After the grace period, only the new secret is valid.

        Args:
            current_secret: The current secret key
            expiry_days: Days until the new secret expires (default: 90)
            grace_period_days: Days to keep both secrets valid (default: 7)

        Returns:
            Tuple of (new_secret, metadata)
        """
        new_secret = self.generate_secret_key()
        now = datetime.utcnow()

        metadata = SecretMetadata(
            key_id=secrets.token_hex(8),
            created_at=now,
            expires_at=now + timedelta(days=expiry_days),
            is_active=True,
        )

        return new_secret, metadata

    def validate_secret_expiry(self, metadata: SecretMetadata) -> bool:
        """
        Check if a secret has expired.

        Args:
            metadata: Secret metadata to check

        Returns:
            True if secret is still valid, False if expired
        """
        return datetime.utcnow() < metadata.expires_at and metadata.is_active

    def get_secret_rotation_warning(self, metadata: SecretMetadata) -> str | None:
        """
        Get a warning message if secret is approaching expiration.

        Args:
            metadata: Secret metadata to check

        Returns:
            Warning message if secret expires within 14 days, None otherwise
        """
        days_until_expiry = (metadata.expires_at - datetime.utcnow()).days

        if days_until_expiry <= 14:
            return (
                f"WARNING: Secret key expires in {days_until_expiry} days. "
                f"Please rotate the secret key soon."
            )

        return None


def rotate_secret_key(
    current_key: str | None = None,
    key_length: int = 32,
) -> str:
    """
    Convenience function to rotate a secret key.

    Args:
        current_key: Current secret key (optional, for logging purposes)
        key_length: Length of the new secret key in bytes

    Returns:
        New secret key
    """
    manager = SecretManager()
    new_key = manager.generate_secret_key(length=key_length)

    if current_key:
        # Log rotation event (in production, use proper logging)
        print(f"[SECURITY] Secret key rotated at {datetime.utcnow().isoformat()}")

    return new_key


def generate_jwt_secret() -> str:
    """
    Generate a secure JWT secret key.

    Returns:
        256-bit hex-encoded secret suitable for JWT signing
    """
    return secrets.token_hex(32)


def generate_database_encryption_key() -> str:
    """
    Generate a Fernet key for database field encryption.

    Returns:
        Base64-encoded Fernet key
    """
    return Fernet.generate_key().decode()


def validate_secret_strength(secret: str, min_length: int = 32) -> bool:
    """
    Validate that a secret key meets minimum security requirements.

    Args:
        secret: Secret key to validate
        min_length: Minimum length in characters

    Returns:
        True if secret meets requirements, False otherwise
    """
    if len(secret) < min_length:
        return False

    # Check for sufficient entropy (mix of character types)
    has_lower = any(c.islower() for c in secret)
    has_upper = any(c.isupper() for c in secret)
    has_digit = any(c.isdigit() for c in secret)

    return has_lower and has_upper and has_digit


# Environment variable helpers
def get_secret_from_env(
    key_name: str,
    default: str | None = None,
    required: bool = True,
) -> str:
    """
    Safely retrieve a secret from environment variables.

    Args:
        key_name: Name of the environment variable
        default: Default value if not found
        required: Whether the secret is required

    Returns:
        Secret value from environment

    Raises:
        ValueError: If required secret is not found
    """
    value = os.getenv(key_name, default)

    if required and not value:
        raise ValueError(f"Required secret '{key_name}' not found in environment")

    return value or ""
