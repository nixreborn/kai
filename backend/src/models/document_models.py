"""Pydantic models for document endpoints."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""

    id: UUID
    journal_entry_id: UUID
    user_id: UUID
    file_name: str
    file_type: str
    file_size: int
    file_category: str
    extracted_text: str | None
    metadata: dict[str, Any]
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class DocumentResponse(BaseModel):
    """Response model for document retrieval."""

    id: UUID
    journal_entry_id: UUID
    user_id: UUID
    file_name: str
    file_type: str
    file_size: int
    file_category: str
    extracted_text: str | None
    metadata: dict[str, Any]
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    """Response model for list of documents."""

    documents: list[DocumentResponse]
    total: int


class DocumentAnalysisResponse(BaseModel):
    """Response model for document text analysis."""

    document_id: UUID
    extracted_text: str
    text_length: int
    insights: list[str] = Field(default_factory=list, description="AI-generated insights from content")
