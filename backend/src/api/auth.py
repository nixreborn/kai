"""Authentication API routes."""

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth import get_password_hash, verify_password
from src.auth.dependencies import get_current_active_user, get_current_user
from src.auth.jwt_handler import create_access_token
from src.auth.schemas import (
    MessageResponse,
    PasswordChange,
    Token,
    UserLogin,
    UserRegister,
    UserResponse,
)
from src.core.config import settings
from src.models.database import Session, User, UserProfile
from src.models.db_session import get_db
from src.security.encryption import (
    rotate_encryption_key,
    setup_user_encryption,
)
from src.security.rate_limiter import RateLimits, limiter
from src.security.validators import validate_email_format, validate_password_strength

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimits.REGISTER)
async def register(
    request: Request,
    user_data: UserRegister,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Created user

    Raises:
        HTTPException: If email already exists
    """
    # Validate email format
    email_valid, email_or_error = validate_email_format(user_data.email)
    if not email_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid email format: {email_or_error}",
        )

    # Validate password strength
    password_result = validate_password_strength(user_data.password)
    if not password_result.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password validation failed: {'; '.join(password_result.errors)}",
        )

    # Check if user already exists
    result = await db.execute(select(User).where(User.email == email_or_error))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)

    # Set up encryption for the user
    user_salt, encryption_key, key_hash = setup_user_encryption(user_data.password)

    new_user = User(
        email=email_or_error,  # Use validated email
        password_hash=hashed_password,
        is_active=True,
        encryption_salt=user_salt,
        encryption_key_hash=key_hash,
    )

    db.add(new_user)
    await db.flush()  # Flush to get the user ID

    # Create user profile
    user_profile = UserProfile(
        user_id=new_user.id,
        traits={},
        communication_style=None,
        preferences={},
    )

    db.add(user_profile)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
@limiter.limit(RateLimits.LOGIN)
async def login(
    request: Request,
    user_data: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """
    Authenticate user and return JWT token.

    Args:
        user_data: User login credentials
        db: Database session

    Returns:
        JWT access token

    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()

    # Verify credentials
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    # Create session record
    session = Session(
        user_id=user.id,
        token=access_token,
        expires_at=datetime.utcnow() + access_token_expires,
    )
    db.add(session)
    await db.commit()

    return Token(access_token=access_token, token_type="bearer")


@router.post("/refresh", response_model=Token)
@limiter.limit(RateLimits.REFRESH)
async def refresh_token(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """
    Refresh JWT token for authenticated user.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        New JWT access token
    """
    # Create new access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(current_user.id)}, expires_delta=access_token_expires
    )

    # Create new session record
    session = Session(
        user_id=current_user.id,
        token=access_token,
        expires_at=datetime.utcnow() + access_token_expires,
    )
    db.add(session)
    await db.commit()

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Get current authenticated user information.

    Args:
        current_user: Current authenticated user

    Returns:
        User information
    """
    return current_user


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """
    Logout user and invalidate all sessions.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message
    """
    # Delete all user sessions (this invalidates all tokens)
    result = await db.execute(select(Session).where(Session.user_id == current_user.id))
    sessions = result.scalars().all()

    for session in sessions:
        await db.delete(session)

    await db.commit()

    return MessageResponse(message="Successfully logged out")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """
    Change user password and rotate encryption keys.

    This endpoint:
    1. Verifies the old password
    2. Updates the password hash
    3. Rotates encryption keys for all encrypted journal entries
    4. Invalidates all existing sessions (user must login again)

    Args:
        password_data: Old and new passwords
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If old password is incorrect or key rotation fails
    """
    # Verify old password
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect old password",
        )

    # Update password hash
    new_password_hash = get_password_hash(password_data.new_password)
    current_user.password_hash = new_password_hash

    # Rotate encryption keys if user has encryption set up
    if current_user.encryption_salt and current_user.encryption_key_hash:
        from src.models.database import JournalEntry

        # Get all encrypted journal entries
        entries_query = select(JournalEntry).where(
            JournalEntry.user_id == current_user.id, JournalEntry.is_encrypted == True
        )
        entries_result = await db.execute(entries_query)
        encrypted_entries = list(entries_result.scalars().all())

        # Rotate keys for each entry
        for entry in encrypted_entries:
            if entry.encrypted_content:
                try:
                    new_encrypted_content, new_key, new_key_hash = rotate_encryption_key(
                        password_data.old_password,
                        password_data.new_password,
                        current_user.encryption_salt,
                        entry.encrypted_content,
                    )
                    entry.encrypted_content = new_encrypted_content
                except Exception as e:
                    # If rotation fails, rollback and return error
                    await db.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to rotate encryption keys: {e!s}",
                    ) from e

        # Update user's encryption key hash
        from src.security.encryption import derive_encryption_key, hash_encryption_key

        new_encryption_key = derive_encryption_key(
            password_data.new_password, current_user.encryption_salt
        )
        current_user.encryption_key_hash = hash_encryption_key(new_encryption_key)

    # Invalidate all sessions (user must login again with new password)
    sessions_query = select(Session).where(Session.user_id == current_user.id)
    sessions_result = await db.execute(sessions_query)
    sessions = sessions_result.scalars().all()

    for session in sessions:
        await db.delete(session)

    # Commit all changes
    await db.commit()

    return MessageResponse(
        message="Password changed successfully. Please login again with your new password."
    )
