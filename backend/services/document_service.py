
import aiofiles
import json
import os
import asyncio
from typing import List, Optional
from pathlib import Path
import PyPDF2
import docx
from datetime import datetime
import uuid

from ..models.chat_models import DocumentInfo

class DocumentService:
    def __init__(self):
        self.storage_dir = Path("backend/storage")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.documents_file = self.storage_dir / "documents.json"
        
        # In-memory storage (in production, use a proper database)
        self.documents: List[DocumentInfo] = []
        
        # Load existing documents
        asyncio.create_task(self._load_documents())

    async def _load_documents(self):
        """Load documents from storage"""
        try:
            if self.documents_file.exists():
                async with aiofiles.open(self.documents_file, 'r') as f:
                    content = await f.read()
                    data = json.loads(content)
                    self.documents = [
                        DocumentInfo(**doc) for doc in data
                    ]
        except Exception as e:
            print(f"Error loading documents: {str(e)}")
            self.documents = []

    async def _save_documents(self):
        """Save documents to storage"""
        try:
            data = [doc.dict() for doc in self.documents]
            async with aiofiles.open(self.documents_file, 'w') as f:
                await f.write(json.dumps(data, indent=2, default=str))
        except Exception as e:
            print(f"Error saving documents: {str(e)}")

    def is_valid_file_type(self, filename: str) -> bool:
        """Check if file type is supported"""
        allowed_extensions = {'.pdf', '.doc', '.docx', '.txt'}
        return Path(filename).suffix.lower() in allowed_extensions

    async def extract_text(self, file_path: Path, content_type: str) -> str:
        """Extract text from different file types"""
        try:
            if content_type == 'application/pdf' or file_path.suffix.lower() == '.pdf':
                return await self._extract_pdf_text(file_path)
            elif content_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'] or file_path.suffix.lower() in ['.doc', '.docx']:
                return await self._extract_word_text(file_path)
            elif content_type == 'text/plain' or file_path.suffix.lower() == '.txt':
                return await self._extract_text_file(file_path)
            else:
                return "Unsupported file type for text extraction"
        except Exception as e:
            print(f"Error extracting text from {file_path}: {str(e)}")
            return f"Error extracting text: {str(e)}"

    async def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF files"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            return f"Error reading PDF: {str(e)}"

    async def _extract_word_text(self, file_path: Path) -> str:
        """Extract text from Word documents"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            return f"Error reading Word document: {str(e)}"

    async def _extract_text_file(self, file_path: Path) -> str:
        """Extract text from plain text files"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                async with aiofiles.open(file_path, 'r', encoding='latin-1') as f:
                    return await f.read()
            except Exception as e:
                return f"Error reading text file: {str(e)}"
        except Exception as e:
            return f"Error reading text file: {str(e)}"

    async def store_document(self, document: DocumentInfo):
        """Store document information"""
        self.documents.append(document)
        await self._save_documents()

    async def get_document(self, document_id: str) -> Optional[DocumentInfo]:
        """Get a specific document by ID"""
        for doc in self.documents:
            if doc.id == document_id:
                return doc
        return None

    async def get_all_documents(self) -> List[DocumentInfo]:
        """Get all documents"""
        return self.documents.copy()

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document"""
        for i, doc in enumerate(self.documents):
            if doc.id == document_id:
                # Delete the file
                try:
                    if Path(doc.file_path).exists():
                        Path(doc.file_path).unlink()
                except Exception as e:
                    print(f"Error deleting file {doc.file_path}: {str(e)}")
                
                # Remove from list
                self.documents.pop(i)
                await self._save_documents()
                return True
        return False

    async def search_documents(self, query: str) -> List[DocumentInfo]:
        """Search documents by content or filename"""
        results = []
        query_lower = query.lower()
        
        for doc in self.documents:
            if (query_lower in doc.filename.lower() or 
                query_lower in doc.text_content.lower()):
                results.append(doc)
        
        return results
