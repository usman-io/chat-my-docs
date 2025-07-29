import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';

export default function ApiTest() {
  const [status, setStatus] = useState<string>('idle');
  const [error, setError] = useState<string | null>(null);
  const [documents, setDocuments] = useState<any[]>([]);

  const testConnection = async () => {
    setStatus('loading');
    setError(null);
    
    try {
      // Test health check
      const health = await api.checkHealth();
      console.log('Health check:', health);
      
      // Test getting documents
      const docs = await api.getDocuments();
      console.log('Documents:', docs);
      setDocuments(docs);
      
      setStatus('success');
    } catch (err) {
      console.error('API Test Error:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
      setStatus('error');
    }
  };

  const testFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setStatus('uploading');
    setError(null);

    try {
      const result = await api.uploadDocuments(Array.from(files));
      console.log('Upload result:', result);
      await testConnection(); // Refresh the documents list
      setStatus('upload-success');
    } catch (err) {
      console.error('Upload Error:', err);
      setError(err instanceof Error ? err.message : 'Upload failed');
      setStatus('upload-error');
    }
  };

  useEffect(() => {
    testConnection();
  }, []);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">API Connection Test</h1>
      
      <div className="mb-6 p-4 border rounded-md bg-muted/50">
        <h2 className="text-lg font-semibold mb-2">Connection Status:</h2>
        <div className="flex items-center gap-2">
          <div 
            className={`h-3 w-3 rounded-full ${
              status === 'success' ? 'bg-green-500' : 
              status === 'error' ? 'bg-red-500' : 'bg-yellow-500'
            }`} 
          />
          <span className="capitalize">
            {status === 'loading' ? 'Connecting...' : 
             status === 'success' ? 'Connected' : 
             status === 'error' ? 'Connection failed' : status}
          </span>
        </div>
        
        {error && (
          <div className="mt-2 p-2 bg-red-100 text-red-800 text-sm rounded">
            Error: {error}
          </div>
        )}
        
        <Button 
          onClick={testConnection} 
          className="mt-4"
          disabled={status === 'loading'}
        >
          {status === 'loading' ? 'Testing...' : 'Test Connection'}
        </Button>
      </div>

      <div className="mb-6">
        <h2 className="text-lg font-semibold mb-2">Test File Upload</h2>
        <input 
          type="file" 
          onChange={testFileUpload} 
          multiple 
          disabled={status === 'uploading'}
          className="block w-full text-sm text-gray-500
            file:mr-4 file:py-2 file:px-4
            file:rounded-md file:border-0
            file:text-sm file:font-semibold
            file:bg-primary file:text-primary-foreground
            hover:file:bg-primary/90"
        />
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-2">Documents in the system:</h2>
        {documents.length === 0 ? (
          <p>No documents found</p>
        ) : (
          <div className="space-y-2">
            {documents.map(doc => (
              <div key={doc.id} className="p-3 border rounded-md">
                <h3 className="font-medium">{doc.original_filename}</h3>
                <p className="text-sm text-muted-foreground">
                  ID: {doc.id} • {(doc.size / 1024).toFixed(1)} KB • {new Date(doc.upload_date).toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
      
      <div className="mt-8 p-4 bg-muted rounded-md">
        <h2 className="font-semibold mb-2">Debug Information:</h2>
        <pre className="text-xs bg-black/80 text-white p-3 rounded overflow-auto">
          {JSON.stringify({
            apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'Not set',
            nodeEnv: import.meta.env.MODE,
            documentsCount: documents.length,
            lastUpdated: new Date().toISOString()
          }, null, 2)}
        </pre>
      </div>
    </div>
  );
}
