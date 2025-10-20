"""Document endpoints for managing file uploads."""

from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.dependencies import get_current_user
from ..core.database import get_db
from ..models.database import Document, JournalEntry, User
from ..models.document_models import (
    DocumentAnalysisResponse,
    DocumentListResponse,
    DocumentResponse,
    DocumentUploadResponse,
)
from ..services.file_storage import file_storage_service

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    journal_entry_id: UUID = Form(..., description="Journal entry ID"),
    file: UploadFile = File(..., description="File to upload"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Document:
    """
    Upload a document or image for a journal entry.

    Supports:
    - Images: JPG, PNG (max 10MB)
    - Documents: PDF, TXT, MD (max 20MB)

    Files are validated, stored securely, and associated with the journal entry.
    For PDFs, text extraction is attempted for AI analysis.
    """
    # Verify journal entry exists and belongs to user
    query = select(JournalEntry).where(
        JournalEntry.id == journal_entry_id,
        JournalEntry.user_id == current_user.id,
    )
    result = await db.execute(query)
    journal_entry = result.scalar_one_or_none()

    if not journal_entry:
        raise HTTPException(
            status_code=404,
            detail="Journal entry not found or access denied",
        )

    # Save file using storage service
    try:
        file_path, file_type, file_size = await file_storage_service.save_file(file)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file: {e!s}",
        ) from e

    # Determine file category
    file_category = "image" if file_type.startswith("image/") else "document"

    # Extract text from PDF if applicable
    extracted_text = None
    metadata: dict[str, int | str] = {}

    if file_type == "application/pdf":
        abs_file_path = file_storage_service.get_file_path(file_path)
        extracted_text = file_storage_service.extract_text_from_pdf(abs_file_path)

    # Get image metadata if applicable
    if file_category == "image":
        abs_file_path = file_storage_service.get_file_path(file_path)
        metadata = file_storage_service.get_image_metadata(abs_file_path)

    # Create database entry
    document = Document(
        journal_entry_id=journal_entry_id,
        user_id=current_user.id,
        file_path=file_path,
        file_name=file.filename or "unknown",
        file_type=file_type,
        file_size=file_size,
        file_category=file_category,
        extracted_text=extracted_text,
        metadata=metadata,
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    return document


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document_metadata(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Document:
    """Get document metadata by ID."""
    query = select(Document).where(
        Document.id == document_id,
        Document.user_id == current_user.id,
    )
    result = await db.execute(query)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found or access denied",
        )

    return document


@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Download a document file."""
    # Get document from database
    query = select(Document).where(
        Document.id == document_id,
        Document.user_id == current_user.id,
    )
    result = await db.execute(query)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found or access denied",
        )

    # Get file path
    try:
        file_path = file_storage_service.get_file_path(document.file_path)
    except HTTPException:
        raise

    # Return file
    return FileResponse(
        path=file_path,
        filename=document.file_name,
        media_type=document.file_type,
    )


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a document."""
    # Get document from database
    query = select(Document).where(
        Document.id == document_id,
        Document.user_id == current_user.id,
    )
    result = await db.execute(query)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found or access denied",
        )

    # Delete file from storage
    try:
        file_storage_service.delete_file(document.file_path)
    except HTTPException:
        # Log warning but continue with database deletion
        pass

    # Delete from database
    await db.delete(document)
    await db.commit()


@router.get("/journal/{entry_id}/documents", response_model=DocumentListResponse)
async def list_entry_documents(
    entry_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentListResponse:
    """List all documents for a journal entry."""
    # Verify journal entry exists and belongs to user
    query = select(JournalEntry).where(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == current_user.id,
    )
    result = await db.execute(query)
    journal_entry = result.scalar_one_or_none()

    if not journal_entry:
        raise HTTPException(
            status_code=404,
            detail="Journal entry not found or access denied",
        )

    # Get all documents for the entry
    query = select(Document).where(
        Document.journal_entry_id == entry_id,
        Document.user_id == current_user.id,
    ).order_by(Document.uploaded_at.desc())

    result = await db.execute(query)
    documents = list(result.scalars().all())

    return DocumentListResponse(
        documents=documents,
        total=len(documents),
    )


@router.get("/{document_id}/analysis", response_model=DocumentAnalysisResponse)
async def analyze_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentAnalysisResponse:
    """
    Analyze document content and extract insights.

    For PDFs, returns extracted text and AI-generated insights.
    For images, could include OCR in future versions.
    """
    # Get document from database
    query = select(Document).where(
        Document.id == document_id,
        Document.user_id == current_user.id,
    )
    result = await db.execute(query)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found or access denied",
        )

    # Get extracted text
    extracted_text = document.extracted_text or ""

    if not extracted_text and document.file_type == "application/pdf":
        # Try extracting text again if not already done
        try:
            file_path = file_storage_service.get_file_path(document.file_path)
            extracted_text = file_storage_service.extract_text_from_pdf(file_path)

            # Update document with extracted text
            document.extracted_text = extracted_text
            await db.commit()
        except Exception as e:
            extracted_text = f"Error extracting text: {e!s}"

    # Generate basic insights
    insights = []
    if extracted_text and len(extracted_text) > 100:
        insights.append(f"Document contains {len(extracted_text.split())} words")
        insights.append(f"Estimated reading time: {len(extracted_text.split()) // 200} minutes")

        # Could integrate with AI agents here for deeper analysis
        # For now, just basic text statistics
        if "goal" in extracted_text.lower():
            insights.append("Document mentions goals - consider reviewing for wellness planning")
        if "feel" in extracted_text.lower() or "emotion" in extracted_text.lower():
            insights.append("Document contains emotional content - may be relevant for mood tracking")

    return DocumentAnalysisResponse(
        document_id=document.id,
        extracted_text=extracted_text,
        text_length=len(extracted_text),
        insights=insights,
    )
