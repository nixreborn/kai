"""Helper functions for journal entry encryption.

This module provides utilities for encrypting and decrypting journal entries
with proper error handling and user authentication.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import JournalEntry, User
from .encryption import EncryptionService, decrypt_data, encrypt_data


async def get_user_encryption_service(
    user_id: str, password: str, db: AsyncSession
) -> Optional[EncryptionService]:
    """Get encryption service for a user.

    Args:
        user_id: User ID
        password: User's password for key derivation
        db: Database session

    Returns:
        EncryptionService if user has encryption set up, None otherwise
    """
    # Get user from database
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not user.encryption_salt or not user.encryption_key_hash:
        return None

    # Create encryption service
    return EncryptionService(password, user.encryption_salt)


async def encrypt_journal_entry(
    entry: JournalEntry, encryption_service: EncryptionService
) -> None:
    """Encrypt a journal entry's content.

    Args:
        entry: Journal entry to encrypt
        encryption_service: Encryption service with user's key

    Note:
        This modifies the entry in place.
    """
    if entry.content and not entry.is_encrypted:
        # Encrypt the content
        entry.encrypted_content = encryption_service.encrypt(entry.content)
        entry.is_encrypted = True
        # Clear plain text content
        entry.content = None


async def decrypt_journal_entry(
    entry: JournalEntry, encryption_service: EncryptionService
) -> str:
    """Decrypt a journal entry's content.

    Args:
        entry: Journal entry to decrypt
        encryption_service: Encryption service with user's key

    Returns:
        Decrypted content

    Note:
        This does not modify the entry in the database.
    """
    if entry.is_encrypted and entry.encrypted_content:
        return encryption_service.decrypt(entry.encrypted_content)
    elif entry.content:
        # Entry not encrypted, return plain content
        return entry.content
    return ""


async def decrypt_journal_entry_in_place(
    entry: JournalEntry, encryption_service: EncryptionService
) -> None:
    """Decrypt a journal entry and populate the content field.

    Args:
        entry: Journal entry to decrypt
        encryption_service: Encryption service with user's key

    Note:
        This modifies the entry's content field but does not save to database.
        Used for API responses.
    """
    if entry.is_encrypted and entry.encrypted_content:
        entry.content = encryption_service.decrypt(entry.encrypted_content)
    elif not entry.content:
        entry.content = ""


def can_encrypt_journal(user: User) -> bool:
    """Check if a user has encryption configured.

    Args:
        user: User model

    Returns:
        True if user can encrypt journals, False otherwise
    """
    return bool(user.encryption_salt and user.encryption_key_hash)
