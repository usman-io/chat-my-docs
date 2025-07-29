from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v1", tags=["test"])

@router.get("/test-cors")
async def test_cors():
    """Test CORS configuration"""
    return {"message": "CORS test successful"}

@router.options("/test-cors")
async def test_cors_options():
    """Handle CORS preflight"""
    response = JSONResponse(content={"message": "CORS preflight successful"})
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response
