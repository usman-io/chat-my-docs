// Use environment variable if available, otherwise default to localhost
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Helper function to handle API responses
async function handleResponse<T>(response: Response): Promise<T> {
  const data = await response.json().catch(() => ({}));
  
  if (!response.ok) {
    const errorMessage = data.detail || response.statusText || 'An error occurred';
    console.error(`API Error (${response.status}):`, errorMessage);
    throw new Error(errorMessage);
  }
  
  return data;
}

export interface Document {
  id: string;
  filename: string;
  original_filename: string;
  content_type: string;
  size: number;
  upload_date: string;
}

interface UploadResponse {
  message: string;
  files: Array<{
    id: string;
    filename: string;
    size: number;
    content_type: string;
  }>;
}

interface ChatResponse {
  response: string;
  sources: string[];
  timestamp: string;
}

interface ChatRequest {
  message: string;
  user_id?: string;
}

export const api = {
  // Documents
  uploadDocuments: async (files: File[]): Promise<UploadResponse> => {
    console.log('Uploading documents:', files);
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await fetch(`${API_BASE_URL}/documents/upload`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
        headers: {
          // Don't set Content-Type, let the browser set it with the correct boundary
        },
      });
      
      console.log('Upload response status:', response.status);
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        console.error('Upload failed:', error);
        throw new Error(error.detail || 'Failed to upload documents');
      }
      
      return response.json();
    } catch (error) {
      console.error('Upload error:', error);
      throw error;
    }
  },

  getDocuments: async (): Promise<Document[]> => {
    try {
      console.log('Fetching documents from:', `${API_BASE_URL}/documents`);
      const response = await fetch(`${API_BASE_URL}/documents`, {
        credentials: 'include',
      });
      console.log('Documents response status:', response.status);
      return handleResponse<Document[]>(response);
    } catch (error) {
      console.error('Error fetching documents:', error);
      throw error;
    }
  },

  deleteDocument: async (documentId: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete document');
    }
  },

  // Chat
  chat: async (message: string): Promise<ChatResponse> => {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to send message');
    }

    return response.json();
  },

  // Health
  checkHealth: async (): Promise<{ status: string }> => {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  },
};
