
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import asyncio
import aiofiles
from datetime import datetime
import uuid
import mimetypes
from pathlib import Path

# Import our custom modules
from .services.openai_service import OpenAIService
from .services.document_service import DocumentService
from .models.chat_models import ChatRequest, ChatResponse, DocumentInfo

app = FastAPI(title="Document Chatbot API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initialize services
openai_service = OpenAIService()
document_service = DocumentService()

# Ensure upload directory exists
UPLOAD_DIR = Path("backend/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Document Chatbot API is running!"}

@app.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload multiple documents for processing"""
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
            file_path = UPLOAD_DIR / unique_filename
            
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

@app.post("/chat", response_model=ChatResponse)
async def chat_with_documents(request: ChatRequest):
    """Chat with uploaded documents using OpenAI"""
    try:
        # Get all documents for context
        documents = await document_service.get_all_documents()
        
        if not documents:
            return ChatResponse(
                response="I don't have any documents to reference. Please upload some documents first.",
                sources=[]
            )
        
        # Use OpenAI service to get response
        response = await openai_service.chat_with_documents(
            message=request.message,
            documents=documents
        )
        
        return response
        
    except Exception as e:
        print(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/documents")
async def get_documents():
    """Get list of all uploaded documents"""
    try:
        documents = await document_service.get_all_documents()
        return {
            "documents": [
                {
                    "id": doc.id,
                    "filename": doc.filename,
                    "size": doc.size,
                    "content_type": doc.content_type,
                    "upload_date": doc.upload_date.isoformat()
                }
                for doc in documents
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get documents: {str(e)}")

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a specific document"""
    try:
        await document_service.delete_document(document_id)
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "documents_count": len(await document_service.get_all_documents())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
