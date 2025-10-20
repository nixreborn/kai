"""Security dependencies for FastAPI endpoints.

This module provides dependency injection for encryption services
and secure data handling in API endpoints.
"""

from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.dependencies import get_current_active_user
from ..models.database import User
from ..models.db_session import get_db
from .encryption import EncryptionService


async def get_encryption_service(
    current_user: Annotated[User, Depends(get_current_active_user)],
    x_encryption_password: Annotated[Optional[str], Header()] = None,
) -> Optional[EncryptionService]:
    """Get encryption service for the current user.

    This dependency attempts to create an encryption service for the user.
    It requires the user's password to be provided in the X-Encryption-Password header.

    Args:
        current_user: Current authenticated user
        x_encryption_password: User's password from header (optional)

    Returns:
        EncryptionService if user has encryption set up and password provided, None otherwise

    Note:
        This is optional encryption - if not provided, operations continue without encryption
    """
    if not x_encryption_password:
        return None

    if not current_user.encryption_salt or not current_user.encryption_key_hash:
        return None

    # Create encryption service
    service = EncryptionService(x_encryption_password, current_user.encryption_salt)

    # Verify the password is correct
    if not service.verify_key(current_user.encryption_key_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid encryption password",
        )

    return service


async def require_encryption_service(
    current_user: Annotated[User, Depends(get_current_active_user)],
    x_encryption_password: Annotated[Optional[str], Header()] = None,
) -> EncryptionService:
    """Require encryption service for the current user.

    This dependency creates an encryption service and raises an error if not available.

    Args:
        current_user: Current authenticated user
        x_encryption_password: User's password from header

    Returns:
        EncryptionService

    Raises:
        HTTPException: If encryption is not configured or password not provided
    """
    service = await get_encryption_service(current_user, x_encryption_password)

    if service is None:
        if not current_user.encryption_salt or not current_user.encryption_key_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Encryption not configured for this user",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Encryption password required in X-Encryption-Password header",
        )

    return service
