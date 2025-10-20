"""Cryptographic middleware for automatic encryption/decryption.

This middleware provides transparent encryption and decryption of sensitive data
for FastAPI applications. It can be used as a context manager to handle encryption
keys during request processing.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import HTTPException, Request, status

from .encryption import EncryptionService, verify_and_get_encryption_key


class EncryptionContext:
    """Context manager for encryption operations during request processing.

    This class maintains the encryption service for the duration of a request,
    allowing automatic encryption/decryption of data.
    """

    def __init__(self) -> None:
        """Initialize encryption context."""
        self._encryption_service: EncryptionService | None = None

    def set_encryption_service(self, service: EncryptionService) -> None:
        """Set the encryption service for this context.

        Args:
            service: Initialized encryption service
        """
        self._encryption_service = service

    def get_encryption_service(self) -> EncryptionService | None:
        """Get the current encryption service.

        Returns:
            Encryption service if available, None otherwise
        """
        return self._encryption_service

    def clear(self) -> None:
        """Clear the encryption service from context."""
        self._encryption_service = None

    @property
    def is_initialized(self) -> bool:
        """Check if encryption service is initialized."""
        return self._encryption_service is not None


# Global encryption context (thread-safe through FastAPI's async nature)
_encryption_context = EncryptionContext()


def get_encryption_context() -> EncryptionContext:
    """Get the global encryption context.

    Returns:
        Global encryption context instance
    """
    return _encryption_context


@asynccontextmanager
async def encryption_session(
    password: str, user_salt: str, stored_key_hash: str
) -> AsyncGenerator[EncryptionService, None]:
    """Create an encryption session with automatic cleanup.

    This context manager initializes an encryption service, verifies the password,
    and ensures proper cleanup after use.

    Args:
        password: User's password
        user_salt: User's salt from database
        stored_key_hash: Stored key hash for verification

    Yields:
        EncryptionService instance

    Raises:
        HTTPException: If password verification fails
    """
    # Verify password and get encryption key
    encryption_key = verify_and_get_encryption_key(password, user_salt, stored_key_hash)

    if encryption_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid encryption credentials",
        )

    # Create encryption service
    service = EncryptionService(password, user_salt)

    # Set in global context
    context = get_encryption_context()
    context.set_encryption_service(service)

    try:
        yield service
    finally:
        # Clean up
        context.clear()


def get_current_encryption_service() -> EncryptionService | None:
    """Get the encryption service from the current context.

    This is useful for dependency injection in FastAPI endpoints.

    Returns:
        Current encryption service if available, None otherwise
    """
    return get_encryption_context().get_encryption_service()


def require_encryption_service() -> EncryptionService:
    """Get the encryption service or raise an error if not available.

    This is useful for endpoints that require encryption.

    Returns:
        Current encryption service

    Raises:
        HTTPException: If no encryption service is available in context
    """
    service = get_current_encryption_service()
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Encryption service not initialized. Please provide authentication.",
        )
    return service


class CryptoMiddleware:
    """Middleware for handling encryption context in requests.

    This middleware can be added to FastAPI applications to provide
    automatic encryption context management for requests.
    """

    def __init__(self, app):
        """Initialize middleware.

        Args:
            app: FastAPI application instance
        """
        self.app = app

    async def __call__(self, request: Request, call_next):
        """Process request with encryption context.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware in chain

        Returns:
            HTTP response
        """
        # Check if request contains encryption credentials in headers
        # This is optional - encryption can also be set up per-endpoint
        encryption_password = request.headers.get("X-Encryption-Password")
        encryption_salt = request.headers.get("X-Encryption-Salt")
        key_hash = request.headers.get("X-Encryption-Key-Hash")

        if encryption_password and encryption_salt and key_hash:
            # Set up encryption context
            try:
                async with encryption_session(
                    encryption_password, encryption_salt, key_hash
                ):
                    response = await call_next(request)
            except HTTPException as e:
                # Return authentication error
                from fastapi.responses import JSONResponse

                return JSONResponse(
                    status_code=e.status_code, content={"detail": e.detail}
                )
        else:
            # Process without encryption context
            response = await call_next(request)

        return response


# Utility decorators and functions


def encrypt_field(data: str, service: EncryptionService | None = None) -> str:
    """Encrypt a field using the current or provided encryption service.

    Args:
        data: Data to encrypt
        service: Encryption service (uses current context if None)

    Returns:
        Encrypted data

    Raises:
        HTTPException: If no encryption service is available
    """
    if service is None:
        service = require_encryption_service()

    return service.encrypt(data)


def decrypt_field(
    encrypted_data: str, service: EncryptionService | None = None
) -> str:
    """Decrypt a field using the current or provided encryption service.

    Args:
        encrypted_data: Encrypted data
        service: Encryption service (uses current context if None)

    Returns:
        Decrypted data

    Raises:
        HTTPException: If no encryption service is available
    """
    if service is None:
        service = require_encryption_service()

    return service.decrypt(encrypted_data)
