"""Authentication API routes."""

from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth import get_password_hash, verify_password
from src.auth.dependencies import get_current_active_user, get_current_user
from src.auth.jwt_handler import create_access_token
from src.auth.schemas import MessageResponse, Token, UserLogin, UserRegister, UserResponse
from src.core.config import settings
from src.models.database import Session, User, UserProfile
from src.models.db_session import get_db

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
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
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        is_active=True,
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
async def login(
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
async def refresh_token(
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
