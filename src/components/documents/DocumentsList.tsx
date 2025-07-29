import { useState } from 'react';
import { FileText, Trash2, Loader2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { Button } from '@/components/ui/button';
import { useDocuments } from '@/contexts/DocumentContext';
import { Skeleton } from '@/components/ui/skeleton';
import { Document } from '@/lib/api';

export function DocumentsList() {
  const { documents, isLoading, deleteDocument } = useDocuments();

  const handleDelete = async (id: string, filename: string) => {
    if (confirm(`Are you sure you want to delete "${filename}"?`)) {
      try {
        await deleteDocument(id);
      } catch (error) {
        console.error('Failed to delete document:', error);
      }
    }
  };

  if (isLoading && documents.length === 0) {
    return (
      <div className="space-y-2">
        {[...Array(3)].map((_, i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="text-center py-8">
        <FileText className="mx-auto h-12 w-12 text-muted-foreground" />
        <h3 className="mt-2 text-sm font-medium">No documents</h3>
        <p className="mt-1 text-sm text-muted-foreground">
          Get started by uploading a document.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {documents.map((doc) => (
        <DocumentItem
          key={doc.id}
          document={doc}
          onDelete={handleDelete}
        />
      ))}
    </div>
  );
}

function DocumentItem({
  document,
  onDelete,
}: {
  document: Document;
  onDelete: (id: string, filename: string) => void;
}) {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    try {
      setIsDeleting(true);
      await onDelete(document.id, document.original_filename);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="flex items-center justify-between p-3 border rounded-md hover:bg-muted/50">
      <div className="flex items-center space-x-3">
        <div className="p-2 rounded-md bg-primary/10">
          <FileText className="h-5 w-5 text-primary" />
        </div>
        <div className="min-w-0">
          <p className="text-sm font-medium truncate">
            {document.original_filename}
          </p>
          <div className="flex items-center space-x-2 text-xs text-muted-foreground">
            <span>{(document.size / 1024).toFixed(1)} KB</span>
            <span>•</span>
            <span>
              {formatDistanceToNow(new Date(document.upload_date), {
                addSuffix: true,
              })}
            </span>
          </div>
        </div>
      </div>
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8"
        onClick={handleDelete}
        disabled={isDeleting}
      >
        {isDeleting ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Trash2 className="h-4 w-4 text-destructive" />
        )}
      </Button>
    </div>
  );
}
