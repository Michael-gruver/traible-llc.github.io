import { Button } from "@/components/ui/button";
import { useRecoilState, atom } from "recoil";
import { useEffect, useState } from "react";
import { formatDistanceToNow } from "date-fns";
import { documentIdState, selectedConversationIdState } from "@/store/chat";
import { Trash2 } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { LoadingSpinner } from "@/components/ui/loading-spinner";

interface Conversation {
  id: string;
  title: string;
  created_at: string;
  documents: { id: string }[];
}

export const conversationsState = atom<Conversation[]>({
  key: "conversationsState",
  default: [],
});

export default function ConversationList() {
  const [conversations, setConversations] = useRecoilState(conversationsState);
  const [selectedConversationId, setSelectedConversationId] = useRecoilState(selectedConversationIdState);
  const [documentIds, setDocumentId] = useRecoilState(documentIdState);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const { toast } = useToast();
  const url = import.meta.env.VITE_API_URL;

  useEffect(() => {
    fetchConversations();
  }, [setConversations]);

     const fetchConversations = async () => {
       try {
         const token = localStorage.getItem("token");
         const response = await fetch(`${url}/api/conversations/`, {
           headers: {
             Authorization: `Bearer ${token}`,
           },
         });
         const data = await response.json();
         setConversations(data.conversations);
       } catch (error) {
         console.error("Failed to fetch conversations:", error);
       }
     };

  const handleSelectConversation = (id: string, documentIds: string[]) => {
    console.log("Selected conversation ID:", id);
    if (documentIds.length > 0) {
      setDocumentId(documentIds);
    }
    setSelectedConversationId(id);
  };

  const handleDeleteConversation = async (id: string) => {
    try {
      setIsDeleting(true);
      const token = localStorage.getItem("token");
      const response = await fetch(`${url}/api/conversations/${id}/delete/`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setConversations(conversations.filter(conv => conv.id !== id));
        if (selectedConversationId === id) {
          setSelectedConversationId("");
          setDocumentId([]);
        }
        toast({
          title: "Success",
          description: "Conversation deleted successfully",
        });
      } else {
        console.error("Failed to delete conversation:", await response.text());
      }
    } catch (error) {
      console.error("Error deleting conversation:", error);
    } finally {
      setIsDeleting(false);
      setDeleteId(null);
    }
  };

  return (
    <div className="space-y-4 p-4 border rounded-lg shadow-md ">
      <h3 className="text-lg font-semibold text-muted-foreground">
        Conversation History
      </h3>
      <div className="flex flex-col gap-2">
        {conversations?.length > 0 ? (
          conversations.map(({ id, title, created_at, documents }) => (
            <Button
              key={id}
              variant="outline"
              className="justify-between text-left w-full group"
              onClick={() =>
                handleSelectConversation(
                  id,
                  documents.map((doc) => doc.id)
                )
              }
            >
              <div className="flex-1">
                <p
                  className="font-medium text-sm truncate w-full max-w-[40%]"
                  title={title}
                >
                  {title}
                </p>
                <p className="text-xs text-muted-foreground">
                  {formatDistanceToNow(new Date(created_at), {
                    addSuffix: true,
                  })}
                </p>
              </div>
              <Dialog
                open={deleteId === id}
                onOpenChange={(open) => setDeleteId(open ? id : null)}
              >
                <DialogTrigger asChild>
                  <span
                    onClick={(e) => e.stopPropagation()}
                    className="text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <Trash2 className="h-4 w-4" />
                  </span>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[425px] rounded-lg shadow-lg">
                  <DialogHeader>
                    <DialogTitle className="text-lg font-semibold text-primary">
                      Delete Conversation
                    </DialogTitle>
                    <DialogDescription className="text-sm text-gray-200">
                      Are you sure you want to delete "{title}"? This action
                      cannot be undone.
                    </DialogDescription>
                  </DialogHeader>
                  <DialogFooter className="mt-4">
                    <Button
                      variant="outline"
                      onClick={() => setDeleteId(null)}
                      className="text-primary hover:bg-primary "
                      disabled={isDeleting}
                    >
                      Cancel
                    </Button>
                    <Button
                      variant="destructive"
                      onClick={() => handleDeleteConversation(id)}
                      className="bg-red-600 hover:bg-red-700 text-white"
                      disabled={isDeleting}
                    >
                      {isDeleting ? <LoadingSpinner /> : "Delete"}
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </Button>
          ))
        ) : (
          <p className="text-sm text-muted-foreground">No conversations yet.</p>
        )}
      </div>
    </div>
  );
}
