"""Input validation and sanitization utilities for Kai backend."""

import re
from typing import Any

from email_validator import EmailNotValidError, validate_email as validate_email_lib
from pydantic import BaseModel, Field, field_validator


class PasswordValidationResult(BaseModel):
    """Result of password validation."""

    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    strength_score: int = Field(ge=0, le=5)


def validate_email_format(email: str) -> tuple[bool, str]:
    """
    Validate email format using email-validator library.

    Args:
        email: Email address to validate

    Returns:
        Tuple of (is_valid, normalized_email or error_message)
    """
    try:
        # Validate and normalize email
        valid = validate_email_lib(email, check_deliverability=False)
        return True, valid.normalized
    except EmailNotValidError as e:
        return False, str(e)


def validate_password_strength(password: str) -> PasswordValidationResult:
    """
    Validate password strength with enhanced requirements.

    Requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    - No common passwords
    - No sequential characters

    Args:
        password: Password to validate

    Returns:
        PasswordValidationResult with validation status and errors
    """
    errors: list[str] = []
    strength_score = 0

    # Length check
    if len(password) < 12:
        errors.append("Password must be at least 12 characters long")
    elif len(password) >= 16:
        strength_score += 1
    if len(password) >= 12:
        strength_score += 1

    # Uppercase check
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")
    else:
        strength_score += 1

    # Lowercase check
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")
    else:
        strength_score += 1

    # Digit check
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one digit")
    else:
        strength_score += 1

    # Special character check
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/;\'`~]', password):
        errors.append("Password must contain at least one special character")
    else:
        strength_score += 1

    # Check for common passwords
    common_passwords = {
        "password123",
        "123456789",
        "qwerty123",
        "admin123456",
        "welcome123",
        "letmein123",
        "password1234",
        "abc123456789",
    }

    if password.lower() in common_passwords:
        errors.append("Password is too common")
        strength_score = max(0, strength_score - 2)

    # Check for sequential characters
    sequential_patterns = [
        "123456",
        "abcdef",
        "qwerty",
        "asdfgh",
        "zxcvbn",
    ]

    password_lower = password.lower()
    for pattern in sequential_patterns:
        if pattern in password_lower:
            errors.append("Password contains sequential characters")
            strength_score = max(0, strength_score - 1)
            break

    # Cap strength score at 5
    strength_score = min(5, strength_score)

    return PasswordValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        strength_score=strength_score,
    )


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize user input to prevent XSS and injection attacks.

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Truncate to max length
    text = text[:max_length]

    # Remove null bytes
    text = text.replace("\x00", "")

    # Remove control characters except newlines and tabs
    text = "".join(char for char in text if char.isprintable() or char in "\n\t")

    # Escape HTML characters
    html_escape_table = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#x27;",
        "/": "&#x2F;",
    }

    for char, escaped in html_escape_table.items():
        text = text.replace(char, escaped)

    return text.strip()


def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username format.

    Requirements:
    - 3-32 characters
    - Alphanumeric, underscore, and hyphen only
    - Must start with a letter
    - No consecutive special characters

    Args:
        username: Username to validate

    Returns:
        Tuple of (is_valid, error_message or empty string)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"

    if len(username) > 32:
        return False, "Username must be at most 32 characters long"

    if not username[0].isalpha():
        return False, "Username must start with a letter"

    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"

    if re.search(r"[_-]{2,}", username):
        return False, "Username cannot contain consecutive special characters"

    return True, ""


def validate_journal_content(content: str, max_length: int = 50000) -> tuple[bool, str]:
    """
    Validate journal entry content.

    Args:
        content: Journal content to validate
        max_length: Maximum allowed length

    Returns:
        Tuple of (is_valid, error_message or empty string)
    """
    if not content or not content.strip():
        return False, "Journal content cannot be empty"

    if len(content) > max_length:
        return False, f"Journal content exceeds maximum length of {max_length} characters"

    # Check for suspicious patterns (potential injection attempts)
    suspicious_patterns = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return False, "Journal content contains potentially unsafe content"

    return True, ""


def validate_chat_message(message: str) -> tuple[bool, str]:
    """
    Validate chat message content.

    Args:
        message: Chat message to validate

    Returns:
        Tuple of (is_valid, error_message or empty string)
    """
    if not message or not message.strip():
        return False, "Message cannot be empty"

    if len(message) > 5000:
        return False, "Message exceeds maximum length of 5000 characters"

    # Basic sanitization check
    if "\x00" in message:
        return False, "Message contains invalid characters"

    return True, ""


class StrongPasswordValidator:
    """Pydantic validator for strong passwords."""

    @classmethod
    def validate_strong_password(cls, value: str) -> str:
        """
        Validate password strength for use with Pydantic models.

        Args:
            value: Password to validate

        Returns:
            The password if valid

        Raises:
            ValueError: If password doesn't meet requirements
        """
        result = validate_password_strength(value)

        if not result.is_valid:
            error_msg = "Password validation failed: " + "; ".join(result.errors)
            raise ValueError(error_msg)

        return value
