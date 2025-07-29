
import openai
import json
import asyncio
import aiofiles
from typing import List, Dict, Any
from datetime import datetime
import uuid
import os
from pathlib import Path

from ..models.chat_models import DocumentInfo, ChatResponse, BatchJob

class OpenAIService:
    def __init__(self):
        # Set your OpenAI API key here
        # In production, use environment variables or secrets management
        self.api_key = "your-openai-api-key-here"  # Replace with your actual API key
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Directory for batch processing files
        self.batch_dir = Path("backend/batch_files")
        self.batch_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory storage for batch jobs (in production, use a database)
        self.batch_jobs: Dict[str, BatchJob] = {}

    async def chat_with_documents(self, message: str, documents: List[DocumentInfo]) -> ChatResponse:
        """
        Chat with documents using OpenAI's batch API for processing multiple documents
        """
        try:
            # For real-time chat, we'll use the regular API
            # For batch processing of multiple documents, we'll use batch API
            
            if len(documents) > 5:  # Use batch API for many documents
                return await self._batch_chat_with_documents(message, documents)
            else:  # Use regular API for few documents
                return await self._realtime_chat_with_documents(message, documents)
                
        except Exception as e:
            print(f"OpenAI service error: {str(e)}")
            return ChatResponse(
                response="I'm sorry, I encountered an error while processing your request. Please try again.",
                sources=[]
            )

    async def _realtime_chat_with_documents(self, message: str, documents: List[DocumentInfo]) -> ChatResponse:
        """Use regular OpenAI API for real-time responses"""
        try:
            # Combine document contents for context
            context = "\n\n".join([
                f"Document: {doc.filename}\nContent: {doc.text_content[:2000]}..."  # Limit content length
                for doc in documents
            ])
            
            # Create the prompt
            system_prompt = """You are a helpful assistant that answers questions based on the provided documents. 
            Always reference the specific documents when answering questions. 
            If the answer cannot be found in the documents, say so clearly."""
            
            user_prompt = f"""Context from uploaded documents:
            {context}
            
            User question: {message}
            
            Please answer based on the document content provided above."""
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            sources = [doc.filename for doc in documents]
            
            return ChatResponse(
                response=answer,
                sources=sources
            )
            
        except Exception as e:
            print(f"Real-time chat error: {str(e)}")
            return ChatResponse(
                response="I'm sorry, I couldn't process your request at the moment. Please try again later.",
                sources=[]
            )

    async def _batch_chat_with_documents(self, message: str, documents: List[DocumentInfo]) -> ChatResponse:
        """Use OpenAI Batch API for processing multiple documents"""
        try:
            # Create batch job
            job_id = str(uuid.uuid4())
            
            # Prepare batch requests
            batch_requests = []
            for i, doc in enumerate(documents):
                request = {
                    "custom_id": f"doc_{i}_{doc.id}",
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": "gpt-4-turbo-preview",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a helpful assistant that answers questions based on document content."
                            },
                            {
                                "role": "user",
                                "content": f"Document: {doc.filename}\nContent: {doc.text_content[:3000]}\n\nQuestion: {message}"
                            }
                        ],
                        "max_tokens": 500
                    }
                }
                batch_requests.append(request)
            
            # Save batch input file
            input_file_path = self.batch_dir / f"batch_input_{job_id}.jsonl"
            async with aiofiles.open(input_file_path, 'w') as f:
                for request in batch_requests:
                    await f.write(json.dumps(request) + '\n')
            
            # Upload file to OpenAI
            with open(input_file_path, 'rb') as f:
                file_response = self.client.files.create(
                    file=f,
                    purpose='batch'
                )
            
            # Create batch job
            batch_response = self.client.batches.create(
                input_file_id=file_response.id,
                endpoint="/v1/chat/completions",
                completion_window="24h"
            )
            
            # Store batch job info
            batch_job = BatchJob(
                job_id=job_id,
                status="in_progress",
                created_at=datetime.now(),
                input_file_id=file_response.id
            )
            self.batch_jobs[job_id] = batch_job
            
            # For now, return a placeholder response
            # In a real implementation, you'd poll for completion or use webhooks
            return ChatResponse(
                response=f"I'm processing your question across {len(documents)} documents. This may take a few moments. Your batch job ID is: {job_id}",
                sources=[doc.filename for doc in documents]
            )
            
        except Exception as e:
            print(f"Batch processing error: {str(e)}")
            return ChatResponse(
                response="I encountered an error while setting up batch processing. Using regular processing instead.",
                sources=[]
            )

    async def check_batch_status(self, job_id: str) -> Dict[str, Any]:
        """Check the status of a batch job"""
        try:
            if job_id not in self.batch_jobs:
                return {"error": "Job not found"}
            
            batch_job = self.batch_jobs[job_id]
            
            # Check with OpenAI
            batch_response = self.client.batches.retrieve(batch_job.input_file_id)
            
            if batch_response.status == "completed":
                # Process results
                output_file_id = batch_response.output_file_id
                if output_file_id:
                    # Download and process results
                    results = await self._process_batch_results(output_file_id)
                    batch_job.status = "completed"
                    batch_job.completed_at = datetime.now()
                    batch_job.output_file_id = output_file_id
                    
                    return {
                        "status": "completed",
                        "results": results
                    }
            
            return {
                "status": batch_response.status,
                "job_id": job_id
            }
            
        except Exception as e:
            return {"error": str(e)}

    async def _process_batch_results(self, output_file_id: str) -> List[Dict[str, Any]]:
        """Process batch results from OpenAI"""
        try:
            # Download the results file
            file_response = self.client.files.content(output_file_id)
            
            results = []
            for line in file_response.text.strip().split('\n'):
                if line:
                    result = json.loads(line)
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error processing batch results: {str(e)}")
            return []

    async def get_batch_jobs(self) -> List[Dict[str, Any]]:
        """Get all batch jobs"""
        return [
            {
                "job_id": job.job_id,
                "status": job.status,
                "created_at": job.created_at.isoformat(),
                "completed_at": job.completed_at.isoformat() if job.completed_at else None
            }
            for job in self.batch_jobs.values()
        ]
