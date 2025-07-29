from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from services.openai_service import OpenAIService
from services.document_service import DocumentService
from models.chat_models import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/v1", tags=["chat"])

# Initialize services
openai_service = OpenAIService()
document_service = DocumentService()

@router.post("/chat", response_model=ChatResponse)
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
