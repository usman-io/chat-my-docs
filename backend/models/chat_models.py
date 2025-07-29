
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[str] = []
    timestamp: datetime = datetime.now()

class DocumentInfo(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_path: str
    content_type: str
    size: int
    upload_date: datetime
    text_content: str

class DocumentResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    content_type: str
    size: int
    upload_date: datetime
    
    class Config:
        from_attributes = True

class BatchJob(BaseModel):
    job_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    input_file_id: str
    output_file_id: Optional[str] = None
    error_message: Optional[str] = None
