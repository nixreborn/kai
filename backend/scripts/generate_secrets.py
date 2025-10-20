#!/usr/bin/env python3
"""Script to generate secure secrets for Kai backend."""

import argparse
import secrets
import sys
from pathlib import Path

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.security.secrets import (
    SecretManager,
    generate_database_encryption_key,
    generate_jwt_secret,
    validate_secret_strength,
)


def generate_all_secrets() -> dict[str, str]:
    """
    Generate all required secrets for the application.

    Returns:
        Dictionary of secret names and their values
    """
    secrets_dict = {
        "SECRET_KEY": generate_jwt_secret(),
        "DATABASE_ENCRYPTION_KEY": generate_database_encryption_key(),
        "SESSION_SECRET": secrets.token_hex(32),
        "CSRF_SECRET": secrets.token_hex(32),
        "API_KEY_SALT": secrets.token_hex(16),
    }

    return secrets_dict


def print_secrets(secrets_dict: dict[str, str], format_type: str = "env") -> None:
    """
    Print secrets in the specified format.

    Args:
        secrets_dict: Dictionary of secrets to print
        format_type: Format type ('env', 'json', 'yaml')
    """
    if format_type == "env":
        print("\n# Generated Secrets - Add these to your .env file")
        print("# Generated at:", secrets.token_hex(4))
        print()
        for key, value in secrets_dict.items():
            print(f"{key}={value}")
        print()

    elif format_type == "json":
        import json

        print(json.dumps(secrets_dict, indent=2))

    elif format_type == "yaml":
        print("# Generated Secrets")
        for key, value in secrets_dict.items():
            print(f"{key}: {value}")

    else:
        raise ValueError(f"Unknown format type: {format_type}")


def validate_secrets(secrets_dict: dict[str, str]) -> bool:
    """
    Validate all generated secrets meet security requirements.

    Args:
        secrets_dict: Dictionary of secrets to validate

    Returns:
        True if all secrets are valid, False otherwise
    """
    all_valid = True

    for key, value in secrets_dict.items():
        is_valid = validate_secret_strength(value, min_length=32)

        if not is_valid:
            print(f"WARNING: {key} does not meet minimum security requirements", file=sys.stderr)
            all_valid = False

    return all_valid


def rotate_secret(secret_name: str) -> str:
    """
    Rotate a specific secret.

    Args:
        secret_name: Name of the secret to rotate

    Returns:
        New secret value
    """
    manager = SecretManager()

    if secret_name == "SECRET_KEY" or secret_name == "JWT_SECRET":
        return generate_jwt_secret()
    elif secret_name == "DATABASE_ENCRYPTION_KEY":
        return generate_database_encryption_key()
    else:
        return manager.generate_secret_key()


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Generate secure secrets for Kai backend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all secrets in ENV format
  python generate_secrets.py

  # Generate secrets in JSON format
  python generate_secrets.py --format json

  # Rotate a specific secret
  python generate_secrets.py --rotate SECRET_KEY

  # Generate a single secret
  python generate_secrets.py --single JWT_SECRET
        """,
    )

    parser.add_argument(
        "--format",
        choices=["env", "json", "yaml"],
        default="env",
        help="Output format (default: env)",
    )

    parser.add_argument(
        "--rotate",
        metavar="SECRET_NAME",
        help="Rotate a specific secret",
    )

    parser.add_argument(
        "--single",
        metavar="SECRET_NAME",
        help="Generate a single secret",
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate generated secrets",
    )

    parser.add_argument(
        "--length",
        type=int,
        default=32,
        help="Length of generated secrets in bytes (default: 32)",
    )

    args = parser.parse_args()

    # Handle single secret generation
    if args.single:
        secret_value = rotate_secret(args.single)
        print(f"{args.single}={secret_value}")
        return

    # Handle secret rotation
    if args.rotate:
        print(f"Rotating {args.rotate}...")
        new_secret = rotate_secret(args.rotate)
        print(f"\nNew {args.rotate}:")
        print(f"{args.rotate}={new_secret}")
        print("\nIMPORTANT: Update your .env file and restart the application.")
        print("Keep the old secret for a grace period to avoid service disruption.")
        return

    # Generate all secrets
    secrets_dict = generate_all_secrets()

    # Validate if requested
    if args.validate:
        if validate_secrets(secrets_dict):
            print("All secrets meet security requirements", file=sys.stderr)
        else:
            print("Some secrets do not meet security requirements", file=sys.stderr)
            sys.exit(1)

    # Print secrets
    print_secrets(secrets_dict, args.format)

    # Print security warnings
    print("\n" + "=" * 70, file=sys.stderr)
    print("SECURITY WARNINGS:", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print("1. Never commit these secrets to version control", file=sys.stderr)
    print("2. Store secrets securely (e.g., .env file, secrets manager)", file=sys.stderr)
    print("3. Rotate secrets regularly (recommended: every 90 days)", file=sys.stderr)
    print("4. Use different secrets for each environment", file=sys.stderr)
    print("5. Back up secrets in a secure location", file=sys.stderr)
    print("=" * 70, file=sys.stderr)


if __name__ == "__main__":
    main()
