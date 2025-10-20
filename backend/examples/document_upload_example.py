"""Example usage of the document upload API.

This script demonstrates how to:
1. Upload a document to a journal entry
2. Retrieve document metadata
3. Download a document
4. List all documents for a journal entry
5. Delete a document

Prerequisites:
- Kai backend server running
- Valid JWT token
- Existing journal entry ID
"""

import httpx
import asyncio
from pathlib import Path


# Configuration
API_BASE_URL = "http://localhost:8000"
JWT_TOKEN = "your-jwt-token-here"  # Replace with actual token
JOURNAL_ENTRY_ID = "your-journal-entry-id"  # Replace with actual entry ID


async def upload_document(file_path: str, journal_entry_id: str) -> dict:
    """Upload a document to a journal entry.

    Args:
        file_path: Path to the file to upload
        journal_entry_id: UUID of the journal entry

    Returns:
        Document metadata
    """
    async with httpx.AsyncClient() as client:
        with open(file_path, "rb") as f:
            files = {"file": (Path(file_path).name, f)}
            data = {"journal_entry_id": journal_entry_id}
            headers = {"Authorization": f"Bearer {JWT_TOKEN}"}

            response = await client.post(
                f"{API_BASE_URL}/api/documents/upload",
                files=files,
                data=data,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()


async def get_document_metadata(document_id: str) -> dict:
    """Get document metadata.

    Args:
        document_id: UUID of the document

    Returns:
        Document metadata
    """
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
        response = await client.get(
            f"{API_BASE_URL}/api/documents/{document_id}",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()


async def download_document(document_id: str, save_path: str) -> None:
    """Download a document.

    Args:
        document_id: UUID of the document
        save_path: Path to save the downloaded file
    """
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
        response = await client.get(
            f"{API_BASE_URL}/api/documents/{document_id}/download",
            headers=headers,
        )
        response.raise_for_status()

        with open(save_path, "wb") as f:
            f.write(response.content)

        print(f"Downloaded to: {save_path}")


async def list_entry_documents(journal_entry_id: str) -> dict:
    """List all documents for a journal entry.

    Args:
        journal_entry_id: UUID of the journal entry

    Returns:
        List of documents
    """
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
        response = await client.get(
            f"{API_BASE_URL}/api/documents/journal/{journal_entry_id}/documents",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()


async def delete_document(document_id: str) -> None:
    """Delete a document.

    Args:
        document_id: UUID of the document
    """
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
        response = await client.delete(
            f"{API_BASE_URL}/api/documents/{document_id}",
            headers=headers,
        )
        response.raise_for_status()
        print(f"Document {document_id} deleted successfully")


async def analyze_document(document_id: str) -> dict:
    """Get text analysis and insights for a document.

    Args:
        document_id: UUID of the document

    Returns:
        Analysis results with extracted text and insights
    """
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
        response = await client.get(
            f"{API_BASE_URL}/api/documents/{document_id}/analysis",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()


async def main():
    """Run example workflow."""
    print("=== Document Upload API Example ===\n")

    try:
        # Example 1: Upload a document
        print("1. Uploading document...")
        document = await upload_document(
            file_path="example_document.pdf",
            journal_entry_id=JOURNAL_ENTRY_ID,
        )
        document_id = document["id"]
        print(f"✓ Uploaded: {document['file_name']} ({document['file_size']} bytes)")
        print(f"  Document ID: {document_id}\n")

        # Example 2: Get document metadata
        print("2. Getting document metadata...")
        metadata = await get_document_metadata(document_id)
        print(f"✓ File: {metadata['file_name']}")
        print(f"  Type: {metadata['file_type']}")
        print(f"  Category: {metadata['file_category']}")
        print(f"  Size: {metadata['file_size']} bytes")
        print(f"  Uploaded: {metadata['uploaded_at']}\n")

        # Example 3: Analyze document (for PDFs)
        if metadata['file_type'] == 'application/pdf':
            print("3. Analyzing document...")
            analysis = await analyze_document(document_id)
            print(f"✓ Extracted {analysis['text_length']} characters")
            print(f"  Insights:")
            for insight in analysis['insights']:
                print(f"    - {insight}")
            print()

        # Example 4: List all documents for the entry
        print("4. Listing all documents for journal entry...")
        documents = await list_entry_documents(JOURNAL_ENTRY_ID)
        print(f"✓ Found {documents['total']} document(s):")
        for doc in documents['documents']:
            print(f"  - {doc['file_name']} ({doc['file_category']})")
        print()

        # Example 5: Download the document
        print("5. Downloading document...")
        await download_document(document_id, f"downloaded_{metadata['file_name']}")
        print()

        # Example 6: Delete the document (optional - commented out)
        # print("6. Deleting document...")
        # await delete_document(document_id)

        print("=== Example completed successfully! ===")

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code}")
        print(f"Details: {e.response.text}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
