import { useState } from 'react';
import { api } from '../lib/api';

export const useFileUpload = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  const uploadFiles = async (files: File[]) => {
    if (!files.length) return [];

    setIsUploading(true);
    setError(null);
    setProgress(0);

    try {
      // In a real app, you might want to implement progress tracking
      // This is a simplified version
      const result = await api.uploadDocuments(files);
      setProgress(100);
      return result.files;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload files';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  return {
    uploadFiles,
    isUploading,
    progress,
    error,
    reset: () => {
      setError(null);
      setProgress(0);
    },
  };
};
