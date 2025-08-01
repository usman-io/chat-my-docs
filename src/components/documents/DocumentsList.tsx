import { useState } from 'react';
import { FileText, Trash2, Loader2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { Button } from '@/components/ui/button';
import { useDocuments } from '@/contexts/DocumentContext';
import { Skeleton } from '@/components/ui/skeleton';
import { Document } from '@/lib/api';
import { toast } from 'sonner';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

export function DocumentsList() {
  const { documents, isLoading, deleteDocument } = useDocuments();

  const handleDelete = async (id: string, filename: string) => {
    try {
      await deleteDocument(id);
      toast.success(`Successfully deleted ${filename}`);
    } catch (error) {
      console.error('Failed to delete document:', error);
      toast.error(`Failed to delete ${filename}`);
      throw error; // Re-throw to allow the DocumentItem to handle the error state
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
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  const handleDelete = async () => {
    try {
      setIsDeleting(true);
      await onDelete(document.id, document.original_filename);
      setShowDeleteDialog(false);
    } finally {
      setIsDeleting(false);
    }
  };

  const openDeleteDialog = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowDeleteDialog(true);
  };

  return (
    <div className="flex items-center justify-between p-3 border rounded-md hover:bg-muted/50">
      <div className="flex items-center space-x-3 max-w-[calc(100%-2rem)]">
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
        className="h-8 w-8 text-muted-foreground hover:text-destructive"
        onClick={openDeleteDialog}
        disabled={isDeleting}
      >
        {isDeleting ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Trash2 className="h-4 w-4" />
        )}
      </Button>
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete document?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <span className="font-medium">{document.original_filename}</span>? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction 
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              disabled={isDeleting}
            >
              {isDeleting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : 'Delete'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
