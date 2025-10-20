# Document Upload System - Implementation Guide

## Overview

The Kai backend now includes a comprehensive document and image upload system that allows users to attach files to their journal entries. The system provides secure file storage, validation, and optional text extraction for AI analysis.

## Features

### File Types Supported
- **Images**: JPG, JPEG, PNG (max 10MB)
- **Documents**: PDF, TXT, MD (max 20MB)

### Security Features
- File type validation using MIME types and extensions
- File size limits
- Filename sanitization with UUID generation
- Path traversal attack prevention
- User ownership verification
- Files stored outside web root

### Advanced Features
- **PDF Text Extraction**: Automatic text extraction from PDF files using PyPDF2
- **Image Metadata**: Extraction of width, height, format information
- **AI Integration Ready**: Extracted text can be passed to AI agents for context
- **Cascade Deletion**: Documents are automatically deleted when parent journal entry is deleted

## Architecture

### Components

1. **File Storage Service** (`src/services/file_storage.py`)
   - Handles file upload, validation, storage, and deletion
   - Manages file system operations
   - Extracts text from PDFs and metadata from images

2. **Database Model** (`src/models/database.py`)
   - `Document` model with relationships to `JournalEntry` and `User`
   - Stores file metadata, extracted text, and custom metadata

3. **API Endpoints** (`src/api/documents.py`)
   - Upload, download, list, delete, and analyze documents
   - Authentication required for all endpoints

4. **Pydantic Models** (`src/models/document_models.py`)
   - Request/response validation
   - Type safety

## API Endpoints

### POST /api/documents/upload
Upload a file for a journal entry.

**Request** (multipart/form-data):
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "journal_entry_id=UUID" \
  -F "file=@/path/to/file.pdf"
```

**Response**:
```json
{
  "id": "uuid",
  "journal_entry_id": "uuid",
  "user_id": "uuid",
  "file_name": "document.pdf",
  "file_type": "application/pdf",
  "file_size": 12345,
  "file_category": "document",
  "extracted_text": "Text content...",
  "metadata": {},
  "uploaded_at": "2025-10-20T14:00:00"
}
```

### GET /api/documents/{document_id}
Get document metadata.

**Response**:
```json
{
  "id": "uuid",
  "journal_entry_id": "uuid",
  "user_id": "uuid",
  "file_name": "image.jpg",
  "file_type": "image/jpeg",
  "file_size": 8192,
  "file_category": "image",
  "extracted_text": null,
  "metadata": {
    "width": 1920,
    "height": 1080,
    "format": "JPEG",
    "mode": "RGB"
  },
  "uploaded_at": "2025-10-20T14:00:00"
}
```

### GET /api/documents/{document_id}/download
Download the file.

**Response**: File download with original filename and content type.

### DELETE /api/documents/{document_id}
Delete a document.

**Response**: 204 No Content

### GET /api/documents/journal/{entry_id}/documents
List all documents for a journal entry.

**Response**:
```json
{
  "documents": [...],
  "total": 5
}
```

### GET /api/documents/{document_id}/analysis
Get text analysis and insights for a document.

**Response**:
```json
{
  "document_id": "uuid",
  "extracted_text": "Full text...",
  "text_length": 1234,
  "insights": [
    "Document contains 234 words",
    "Estimated reading time: 1 minutes"
  ]
}
```

## Database Schema

### documents table
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    journal_entry_id UUID NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    file_size BIGINT NOT NULL,
    file_category VARCHAR(50) NOT NULL,
    extracted_text TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_documents_journal_entry_id ON documents(journal_entry_id);
CREATE INDEX ix_documents_user_id ON documents(user_id);
```

## File Storage Structure

```
backend/
├── uploads/
│   ├── images/
│   │   └── <uuid>.jpg
│   ├── documents/
│   │   └── <uuid>.pdf
│   └── .gitignore
```

## Installation & Setup

### 1. Install Dependencies
Dependencies have been added to `pyproject.toml`:
```bash
# Already included in project dependencies:
# - python-multipart>=0.0.12
# - pypdf2>=3.0.0
# - pillow>=10.0.0
```

### 2. Run Database Migration
```bash
# Apply the migration
alembic upgrade head
```

### 3. Verify Upload Directory
The `uploads/` directory is created automatically by the FileStorageService, but you can verify:
```bash
ls -la uploads/
# Should show: images/ and documents/ subdirectories
```

### 4. Configure (Optional)
The default upload directory is `uploads/` relative to the backend root. To customize:
```python
# In src/services/file_storage.py
file_storage_service = FileStorageService(upload_dir="custom/path")
```

## Security Considerations

### Implemented Security Measures
1. **File Type Validation**: Both extension and MIME type checked
2. **Size Limits**: Different limits for images (10MB) and documents (20MB)
3. **Filename Sanitization**: UUID-based filenames prevent injection
4. **Path Traversal Protection**: Resolves paths and validates they're within upload directory
5. **User Ownership**: All operations verify file belongs to authenticated user
6. **Image Validation**: PIL verifies image integrity before accepting

### Best Practices
- Keep uploads directory outside web root (✓ implemented)
- Use HTTPS in production
- Regular backup of uploads directory
- Monitor disk usage
- Consider cloud storage (S3, etc.) for production at scale

## Integration with AI Agents

The document system is designed to integrate with the existing AI agent system:

```python
# Example: Pass document text to wellness agent
from src.services.file_storage import file_storage_service
from src.agents.wellness_agent import analyze_wellness_patterns

# Get document
document = await db.get(Document, document_id)

# Extract text if not already done
if not document.extracted_text and document.file_type == "application/pdf":
    file_path = file_storage_service.get_file_path(document.file_path)
    document.extracted_text = file_storage_service.extract_text_from_pdf(file_path)

# Pass to AI agent
insights = await analyze_wellness_patterns(
    conversation_history="",
    journal_entries=f"Document content: {document.extracted_text}"
)
```

## Testing

### Manual Testing with curl

**Upload an image:**
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "journal_entry_id=YOUR_JOURNAL_ENTRY_ID" \
  -F "file=@test_image.jpg"
```

**Upload a PDF:**
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "journal_entry_id=YOUR_JOURNAL_ENTRY_ID" \
  -F "file=@test_document.pdf"
```

**Download a file:**
```bash
curl -X GET "http://localhost:8000/api/documents/{document_id}/download" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o downloaded_file.pdf
```

**Test file validation (should fail):**
```bash
# Try uploading unsupported file type
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "journal_entry_id=YOUR_JOURNAL_ENTRY_ID" \
  -F "file=@test.exe"  # Should return 400 error
```

### Automated Testing
Create test files in `tests/test_api/test_documents.py`:

```python
import pytest
from fastapi import UploadFile
from io import BytesIO

async def test_upload_image(client, auth_headers, test_journal_entry):
    """Test image upload."""
    # Create fake image data
    image_data = BytesIO(b"fake image data")
    files = {"file": ("test.jpg", image_data, "image/jpeg")}
    data = {"journal_entry_id": str(test_journal_entry.id)}

    response = await client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files=files,
        data=data
    )
    assert response.status_code == 201
    assert response.json()["file_name"] == "test.jpg"
```

## Future Enhancements

### Potential Additions
1. **OCR for Images**: Use pytesseract for text extraction from images
2. **Cloud Storage**: Integration with AWS S3, Google Cloud Storage
3. **Image Compression**: Automatic compression for large images
4. **Thumbnail Generation**: Create thumbnails for image previews
5. **Virus Scanning**: ClamAV integration for malware detection
6. **Document Preview**: Generate preview images for documents
7. **Batch Upload**: Allow multiple file uploads at once
8. **File Versioning**: Track document versions
9. **Shared Documents**: Allow sharing documents between users
10. **Advanced Text Analysis**: NLP analysis of extracted text

### OCR Implementation Example
```python
# In file_storage.py
import pytesseract
from PIL import Image

def extract_text_from_image(self, file_path: Path) -> str:
    """Extract text from image using OCR."""
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return f"OCR failed: {e!s}"
```

## Troubleshooting

### Common Issues

**Issue**: "File not found" error when downloading
- **Solution**: Check file_path in database matches actual file location
- **Solution**: Verify uploads directory exists and has correct permissions

**Issue**: "Invalid image file" error
- **Solution**: Ensure image is not corrupted
- **Solution**: Check PIL can open the image type

**Issue**: PDF text extraction returns empty string
- **Solution**: Some PDFs are scanned images - need OCR
- **Solution**: Verify PDF is not password protected

**Issue**: Out of disk space
- **Solution**: Monitor uploads directory size
- **Solution**: Implement automatic cleanup of old files
- **Solution**: Move to cloud storage

## Monitoring & Maintenance

### Metrics to Track
- Total storage used
- Number of uploads per day
- Average file sizes
- Failed upload attempts
- File type distribution

### Regular Maintenance Tasks
- Clean up orphaned files (files without database entries)
- Backup uploads directory
- Verify file integrity
- Update security policies
- Monitor disk usage

### Cleanup Script Example
```python
# scripts/cleanup_orphaned_files.py
import os
from pathlib import Path
from sqlalchemy import select
from src.models.database import Document
from src.core.database import get_db

async def cleanup_orphaned_files():
    """Remove files that don't have database entries."""
    async for db in get_db():
        # Get all file paths from database
        result = await db.execute(select(Document.file_path))
        db_files = {row[0] for row in result.all()}

        # Check all files in uploads
        uploads_dir = Path("uploads")
        for file_path in uploads_dir.rglob("*"):
            if file_path.is_file():
                relative_path = str(file_path.relative_to("."))
                if relative_path not in db_files:
                    print(f"Removing orphaned file: {file_path}")
                    file_path.unlink()
```

## Summary

The document upload system is now fully implemented with:
- ✅ Secure file storage service
- ✅ Database models with proper relationships
- ✅ Complete REST API endpoints
- ✅ File validation and security
- ✅ PDF text extraction
- ✅ Image metadata extraction
- ✅ Database migration
- ✅ Upload directory structure
- ✅ Authentication integration

The system is production-ready and can be extended with additional features as needed.
