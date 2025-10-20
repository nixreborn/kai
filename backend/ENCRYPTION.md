# End-to-End Encryption Implementation

## Overview

The Kai mental wellness platform implements end-to-end encryption for sensitive user data, particularly journal entries. This document describes the encryption architecture, security measures, and usage patterns.

## Architecture

### Encryption Method

- **Algorithm**: Fernet symmetric encryption (AES-128-CBC with HMAC-SHA256)
- **Key Derivation**: PBKDF2-HMAC-SHA256 with 600,000 iterations
- **Library**: Python `cryptography` package (version 42.0.0+)

### Security Features

1. **User-Specific Encryption**
   - Each user has a unique salt for key derivation
   - Encryption keys are derived from user password + user salt + server master salt
   - Keys are never stored in the database

2. **Key Derivation Process**
   ```
   User Password + User Salt + Master Salt
        ↓
   PBKDF2-HMAC-SHA256 (600k iterations)
        ↓
   32-byte Encryption Key
        ↓
   SHA256 Hash (stored in DB for verification)
   ```

3. **Data Protection**
   - Journal entry content is encrypted before storage
   - Encrypted data is stored in `encrypted_content` field
   - Plain text `content` field is cleared after encryption
   - `is_encrypted` flag indicates encryption status

4. **Key Rotation**
   - Automatic key rotation when user changes password
   - All encrypted entries are re-encrypted with new key
   - Atomic operation with rollback on failure

## Database Schema

### User Table Additions

```sql
-- Encryption fields in users table
encryption_salt VARCHAR(255)        -- User-specific salt (base64 encoded)
encryption_key_hash VARCHAR(255)    -- SHA256 hash of derived key
```

### Journal Entry Table Additions

```sql
-- Encryption fields in journal_entries table
content TEXT                        -- Plain text (deprecated, nullable)
encrypted_content TEXT              -- Encrypted content (Fernet token)
is_encrypted BOOLEAN                -- Encryption status flag
```

## API Usage

### Setting Up Encryption

Encryption is automatically configured during user registration:

```python
POST /api/auth/register
{
  "email": "user@example.com",
  "password": "secure_password_123"
}

# Server automatically:
# 1. Generates user salt
# 2. Derives encryption key from password
# 3. Stores salt and key hash in database
```

### Creating Encrypted Journal Entries

To create an encrypted journal entry, include the encryption password in the request header:

```python
POST /api/journal/entries
Headers:
  Authorization: Bearer <jwt_token>
  X-Encryption-Password: <user_password>
Body:
{
  "content": "My private thoughts...",
  "mood": "happy",
  "tags": ["gratitude", "reflection"]
}

# Server automatically:
# 1. Derives encryption key from password + user salt
# 2. Encrypts content before storing
# 3. Returns decrypted content in response
```

### Retrieving Encrypted Entries

To retrieve encrypted entries, provide the encryption password:

```python
GET /api/journal/entries
Headers:
  Authorization: Bearer <jwt_token>
  X-Encryption-Password: <user_password>

# Server automatically:
# 1. Fetches encrypted entries
# 2. Decrypts content before returning
# 3. Returns decrypted entries
```

**Without encryption password:**
```python
GET /api/journal/entries
Headers:
  Authorization: Bearer <jwt_token>

# Returns entries with encrypted_content as-is
# Client cannot decrypt without password
```

### Changing Password (Key Rotation)

```python
POST /api/auth/change-password
Headers:
  Authorization: Bearer <jwt_token>
Body:
{
  "old_password": "old_password_123",
  "new_password": "new_password_456"
}

# Server automatically:
# 1. Verifies old password
# 2. Updates password hash
# 3. Rotates encryption keys for ALL encrypted entries
# 4. Invalidates all sessions (requires re-login)
```

## Security Considerations

### Key Management

1. **Never Store Keys**
   - Encryption keys are derived on-demand from passwords
   - Keys exist only in memory during request processing
   - Keys are cleared after request completion

2. **Password Requirements**
   - Minimum 8 characters
   - Used for both authentication and encryption key derivation
   - Changing password triggers automatic key rotation

3. **Salt Management**
   - User salt: 256-bit random value, unique per user
   - Master salt: Server-side constant, adds extra security layer
   - Combined salt ensures unique keys even with same password

### Attack Resistance

1. **Brute Force Protection**
   - PBKDF2 with 600,000 iterations slows down key derivation
   - Each attempt takes ~100-200ms on modern hardware
   - Makes brute force attacks computationally expensive

2. **Key Derivation Isolation**
   - Each user's keys are independent
   - Compromising one user's data doesn't affect others
   - Master salt prevents rainbow table attacks

3. **Data Integrity**
   - Fernet includes HMAC-SHA256 for authentication
   - Detects tampering or corruption
   - Decryption fails if data is modified

### Limitations

1. **Password Dependency**
   - Encryption security depends on password strength
   - Forgotten password = lost data (by design)
   - No password recovery mechanism for encrypted data

2. **Server Trust**
   - Server has access to passwords during authentication
   - True E2E would require client-side encryption
   - Current design balances security with usability

3. **Performance Impact**
   - Key derivation adds ~100-200ms per request
   - Encryption/decryption adds minimal overhead
   - Consider caching strategies for high-volume users

## Implementation Details

### Core Modules

#### `/src/security/encryption.py`
Core encryption functionality:
- `generate_user_salt()` - Create user-specific salt
- `derive_encryption_key()` - Derive key from password
- `encrypt_data()` - Encrypt plain text
- `decrypt_data()` - Decrypt encrypted data
- `rotate_encryption_key()` - Re-encrypt with new key
- `EncryptionService` - Stateful encryption service

#### `/src/security/journal_encryption.py`
Journal-specific encryption helpers:
- `encrypt_journal_entry()` - Encrypt journal entry
- `decrypt_journal_entry_in_place()` - Decrypt for display
- `can_encrypt_journal()` - Check user encryption status

#### `/src/security/dependencies.py`
FastAPI dependency injection:
- `get_encryption_service()` - Optional encryption service
- `require_encryption_service()` - Required encryption service

#### `/src/security/crypto_middleware.py`
Middleware for encryption context management:
- `encryption_session()` - Context manager for encryption
- `EncryptionContext` - Request-scoped encryption state

### Migration

Apply database migration:
```bash
alembic upgrade head
```

This adds:
- `encryption_salt` and `encryption_key_hash` to users table
- `is_encrypted` flag to journal_entries table
- Makes `content` field nullable (uses `encrypted_content` instead)

## Testing

Run encryption tests:
```bash
pytest tests/security/test_encryption.py -v
```

Test coverage includes:
- Basic encryption/decryption
- Key derivation and verification
- Key rotation
- Unicode and edge cases
- Security properties
- Error handling

## Best Practices

### For Developers

1. **Always use EncryptionService**
   - Don't call encrypt/decrypt functions directly
   - Use dependency injection for encryption services
   - Handle missing encryption gracefully

2. **Check Encryption Status**
   - Verify `is_encrypted` flag before accessing content
   - Provide decryption password when needed
   - Don't assume all entries are encrypted

3. **Handle Errors Properly**
   - Catch `DecryptionError` for invalid keys
   - Catch `EncryptionError` for encryption failures
   - Return appropriate HTTP error codes

### For Users

1. **Strong Passwords**
   - Use unique, strong passwords
   - Password protects both account and data
   - Consider password manager

2. **Password Changes**
   - Changing password re-encrypts all data
   - Process may take time with many entries
   - All sessions invalidated, must re-login

3. **Data Recovery**
   - No password recovery for encrypted data
   - Forgotten password = permanent data loss
   - Consider backup strategies if needed

## Future Enhancements

### Planned Improvements

1. **Client-Side Encryption**
   - Move key derivation to client
   - Server never sees encryption password
   - True end-to-end encryption

2. **Key Backup/Recovery**
   - Optional key escrow with recovery questions
   - Split key storage for recovery
   - Balance security with usability

3. **Selective Encryption**
   - User choice per entry
   - Mixed encrypted/unencrypted entries
   - Performance optimization

4. **Multi-Device Key Sync**
   - Secure key synchronization
   - Device-specific keys
   - Revocation mechanism

### Security Roadmap

1. **Hardware Security Modules (HSM)**
   - Protect master salt in HSM
   - Key derivation in secure enclave
   - Enhanced key protection

2. **Audit Logging**
   - Log encryption operations
   - Track key rotation events
   - Security event monitoring

3. **Regular Security Audits**
   - Third-party security review
   - Penetration testing
   - Compliance verification

## References

### Cryptography Standards

- **NIST SP 800-132**: Recommendation for Password-Based Key Derivation
- **OWASP**: Password Storage Cheat Sheet
- **Fernet Spec**: https://github.com/fernet/spec

### Libraries

- **cryptography**: https://cryptography.io/
- **PBKDF2**: https://en.wikipedia.org/wiki/PBKDF2
- **Fernet**: Symmetric encryption with authentication

## Support

For security concerns or questions:
- Review this documentation
- Check test cases for usage examples
- Consult security team for sensitive issues
- Report vulnerabilities responsibly

---

**Last Updated**: 2025-10-20
**Version**: 1.0
**Status**: Production Ready
