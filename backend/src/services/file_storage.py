"""File storage service for managing document and image uploads."""

import mimetypes
import os
import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image
from PyPDF2 import PdfReader


class FileStorageService:
    """Service for managing file uploads, validation, and storage."""

    # File type configurations
    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png"}
    ALLOWED_DOCUMENT_TYPES = {"application/pdf", "text/plain", "text/markdown"}
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".txt", ".md"}

    # Size limits in bytes
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_DOCUMENT_SIZE = 20 * 1024 * 1024  # 20MB

    def __init__(self, upload_dir: str = "uploads") -> None:
        """Initialize file storage service.

        Args:
            upload_dir: Base directory for file uploads
        """
        self.upload_dir = Path(upload_dir)
        self._ensure_upload_directories()

    def _ensure_upload_directories(self) -> None:
        """Ensure upload directories exist."""
        directories = [
            self.upload_dir,
            self.upload_dir / "images",
            self.upload_dir / "documents",
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent directory traversal attacks.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Get extension
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        # Generate unique filename with UUID
        unique_filename = f"{uuid.uuid4()}{ext}"
        return unique_filename

    def _validate_file_type(self, file: UploadFile) -> tuple[str, str]:
        """Validate file type and return category.

        Args:
            file: Upload file object

        Returns:
            Tuple of (category, file_type) where category is 'image' or 'document'

        Raises:
            HTTPException: If file type is not allowed
        """
        # Get file extension
        _, ext = os.path.splitext(file.filename or "")
        ext = ext.lower()

        if ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File extension {ext} not allowed. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}",
            )

        # Determine MIME type
        content_type = file.content_type or mimetypes.guess_type(file.filename or "")[0] or ""

        # Categorize file
        if content_type in self.ALLOWED_IMAGE_TYPES or ext in {".jpg", ".jpeg", ".png"}:
            return "image", content_type
        if content_type in self.ALLOWED_DOCUMENT_TYPES or ext in {".pdf", ".txt", ".md"}:
            return "document", content_type

        raise HTTPException(
            status_code=400,
            detail=f"File type {content_type} not allowed",
        )

    def _validate_file_size(self, file: UploadFile, category: str) -> None:
        """Validate file size.

        Args:
            file: Upload file object
            category: File category ('image' or 'document')

        Raises:
            HTTPException: If file size exceeds limit
        """
        # Get file size
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)

        # Check size limits
        max_size = self.MAX_IMAGE_SIZE if category == "image" else self.MAX_DOCUMENT_SIZE
        if file_size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            raise HTTPException(
                status_code=400,
                detail=f"File size {file_size / (1024 * 1024):.2f}MB exceeds limit of {max_size_mb}MB",
            )

    def _validate_image(self, file_path: Path) -> None:
        """Validate image file by attempting to open it.

        Args:
            file_path: Path to image file

        Raises:
            HTTPException: If image is invalid
        """
        try:
            with Image.open(file_path) as img:
                img.verify()
        except Exception as e:
            # Clean up invalid file
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image file: {e!s}",
            ) from e

    async def save_file(self, file: UploadFile) -> tuple[str, str, int]:
        """Save uploaded file to storage.

        Args:
            file: Upload file object

        Returns:
            Tuple of (file_path, file_type, file_size)

        Raises:
            HTTPException: If validation fails
        """
        # Validate file type
        category, file_type = self._validate_file_type(file)

        # Validate file size
        self._validate_file_size(file, category)

        # Generate unique filename
        safe_filename = self._sanitize_filename(file.filename or "file")

        # Determine storage path
        subdirectory = self.upload_dir / f"{category}s"
        file_path = subdirectory / safe_filename

        # Save file
        try:
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {e!s}",
            ) from e
        finally:
            file.file.close()

        # Additional validation for images
        if category == "image":
            self._validate_image(file_path)

        # Get final file size
        file_size = file_path.stat().st_size

        # Return relative path for database storage
        relative_path = str(file_path.relative_to(self.upload_dir.parent))

        return relative_path, file_type, file_size

    def get_file_path(self, relative_path: str) -> Path:
        """Get absolute file path from relative path.

        Args:
            relative_path: Relative path from project root

        Returns:
            Absolute file path

        Raises:
            HTTPException: If file doesn't exist or path traversal detected
        """
        # Convert to Path and resolve
        file_path = Path(relative_path).resolve()

        # Ensure path is within upload directory
        try:
            file_path.relative_to(self.upload_dir.parent.resolve())
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail="Invalid file path",
            ) from e

        # Check if file exists
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="File not found",
            )

        return file_path

    def delete_file(self, relative_path: str) -> None:
        """Delete file from storage.

        Args:
            relative_path: Relative path from project root

        Raises:
            HTTPException: If file doesn't exist or deletion fails
        """
        file_path = self.get_file_path(relative_path)

        try:
            file_path.unlink()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete file: {e!s}",
            ) from e

    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text content from PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text content
        """
        try:
            reader = PdfReader(str(file_path))
            text_parts = []

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            return "\n\n".join(text_parts)
        except Exception as e:
            # Log error but don't fail the upload
            return f"Error extracting text: {e!s}"

    def get_image_metadata(self, file_path: Path) -> dict[str, int | str]:
        """Get image metadata.

        Args:
            file_path: Path to image file

        Returns:
            Dictionary with image metadata
        """
        try:
            with Image.open(file_path) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format or "unknown",
                    "mode": img.mode,
                }
        except Exception as e:
            return {"error": str(e)}


# Singleton instance
file_storage_service = FileStorageService()
