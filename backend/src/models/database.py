"""SQLAlchemy database models."""

import uuid
from datetime import datetime, timedelta

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class JournalEntry(Base):
    """Journal entry database model."""

    __tablename__ = "journal_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    encrypted_content = Column(Text, nullable=True)  # For future encryption support
    tags = Column(JSON, default=list, nullable=False)  # List of tag strings
    mood = Column(String(50), nullable=True)  # e.g., "happy", "sad", "anxious"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="journal_entries")

    def __repr__(self) -> str:
        """String representation."""
        return f"<JournalEntry(id={self.id}, user_id={self.user_id}, created_at={self.created_at})>"


class User(Base):
    """User database model for authentication."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    journal_entries = relationship("JournalEntry", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation."""
        return f"<User(id={self.id}, email={self.email})>"


class UserProfile(Base):
    """User profile model for storing personalization data."""

    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Genetic Algorithm traits and preferences
    traits = Column(JSON, default=dict, nullable=False)  # User personality traits
    communication_style = Column(String(100), nullable=True)  # e.g., "empathetic", "direct", "supportive"
    preferences = Column(JSON, default=dict, nullable=False)  # User preferences for interactions

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="profile")

    def __repr__(self) -> str:
        """String representation."""
        return f"<UserProfile(id={self.id}, user_id={self.user_id})>"


class Conversation(Base):
    """Conversation model for storing chat history."""

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    messages = Column(JSON, default=list, nullable=False)  # List of message objects
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="conversations")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Conversation(id={self.id}, user_id={self.user_id}, created_at={self.created_at})>"


class Session(Base):
    """Session model for managing user authentication sessions."""

    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Session(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"

    @property
    def is_expired(self) -> bool:
        """Check if the session is expired."""
        return datetime.utcnow() > self.expires_at
