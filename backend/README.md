
# Document Chatbot Backend

This is the FastAPI backend for the Document Chatbot application that uses OpenAI's batch API for processing documents.

## Features

- Document upload and processing (PDF, DOC, DOCX, TXT)
- Text extraction from various document formats
- OpenAI integration with both real-time and batch processing
- RESTful API endpoints for frontend integration
- Document management and storage

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your OpenAI API key in `services/openai_service.py`:
```python
self.api_key = "your-openai-api-key-here"
```

3. Run the server:
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Upload Documents
- **POST** `/upload`
- Upload multiple documents for processing
- Accepts: PDF, DOC, DOCX, TXT files

### Chat with Documents
- **POST** `/chat`
- Send a message to chat with uploaded documents
- Body: `{"message": "your question"}`

### Get Documents
- **GET** `/documents`
- Get list of all uploaded documents

### Delete Document
- **DELETE** `/documents/{document_id}`
- Delete a specific document

### Health Check
- **GET** `/health`
- Check API health status

## OpenAI Batch Processing

The service automatically uses:
- **Real-time API**: For queries with ≤5 documents
- **Batch API**: For queries with >5 documents

Batch processing provides cost-effective handling of large document sets with 24-hour processing windows.

## File Structure

```
backend/
├── main.py              # FastAPI application
├── models/
│   └── chat_models.py   # Pydantic models
├── services/
│   ├── openai_service.py    # OpenAI integration
│   └── document_service.py  # Document processing
├── uploads/             # Uploaded files storage
├── storage/             # Document metadata storage
├── batch_files/         # Batch processing files
└── requirements.txt     # Python dependencies
```

## Environment Variables

In production, set these environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `UPLOAD_DIR`: Directory for file uploads
- `STORAGE_DIR`: Directory for metadata storage

## Notes

- The current implementation uses in-memory storage for simplicity
- For production, replace with a proper database (PostgreSQL, MongoDB, etc.)
- Implement proper authentication and authorization
- Add rate limiting and input validation
- Consider using background tasks for long-running operations
