from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import aiofiles
import uuid
from datetime import datetime
from typing import List

from services.document_service import DocumentService
from models.chat_models import DocumentInfo, DocumentResponse

router = APIRouter(prefix="/api/v1", tags=["documents"])

# Initialize services
document_service = DocumentService()

@router.post("/documents/upload", response_model=List[DocumentResponse])
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload multiple documents for processing
    
    Args:
        files: List of files to upload
        
    Returns:
        List of uploaded document information
    """
    try:
        uploaded_files = []
        
        for file in files:
            # Validate file type
            if not document_service.is_valid_file_type(file.filename):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file type: {file.filename}"
                )
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = Path(file.filename).suffix
            unique_filename = f"{file_id}{file_extension}"
            file_path = Path("uploads") / unique_filename
            
            # Ensure upload directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Extract text content
            text_content = await document_service.extract_text(file_path, file.content_type)
            
            # Store document metadata
            doc_info = DocumentInfo(
                id=file_id,
                filename=file.filename,
                original_filename=file.filename,
                file_path=str(file_path),
                content_type=file.content_type,
                size=len(content),
                upload_date=datetime.now(),
                text_content=text_content
            )
            
            await document_service.store_document(doc_info)
            
            uploaded_files.append({
                "id": file_id,
                "filename": file.filename,
                "size": len(content),
                "content_type": file.content_type
            })
        
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Successfully uploaded {len(uploaded_files)} files",
                "files": uploaded_files
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/documents", response_model=List[DocumentResponse])
async def get_documents():
    """Get list of all uploaded documents"""
    try:
        documents = await document_service.get_all_documents()
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get documents: {str(e)}")

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a specific document"""
    try:
        success = await document_service.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
