// import { useEffect, useState } from "react";
// import { Button } from "@/components/ui/button";
// import { useToast } from "@/hooks/use-toast";
// import { Download, ChevronDown, ChevronUp } from "lucide-react";
// import { useRecoilState } from "recoil";
// import { loaderState } from "@/store/chat";

// interface Document {
//   id: number;
//   title: string;
//   download_url: string;
// }

// export default function DocumentList() {
//   const [documentList, setDocumentList] = useState<Document[]>([]);
//   const [loader, setLoader] = useRecoilState(loaderState);

//   const [isOpen, setIsOpen] = useState(false);
//   const { toast } = useToast();
//   const url = import.meta.env.VITE_API_URL;

//   useEffect(() => {
//     if (isOpen) {
//       fetchDocuments();
//     }
//   }, [isOpen, loader]);

//   const fetchDocuments = async () => {
//     try {
//       const token = localStorage.getItem("token");
//       const response = await fetch(`${url}/api/documentList/list/`, {
//         headers: { Authorization: `Bearer ${token}` },
//       });
//       const data = await response.json();
//       setDocumentList(data.documentList);
//     } catch (error) {
//       console.error("Failed to fetch documentList:", error);
//     }
//   };

//   const handleDownload = async (downloadUrl: string, title: string) => {
//     try {
//       const token = localStorage.getItem("token");
//       const response = await fetch(`${url}${downloadUrl}`, {
//         method: "GET",
//         headers: {
//           Authorization: `Bearer ${token}`,
//         },
//       });

//       if (!response.ok) {
//         toast({
//           title: "Error",
//           description: "Failed to download, please try again later",
//         });
//         return;
//       }
//       const blob = await response.blob();
//       const blobUrl = window.URL.createObjectURL(blob);

//       const a = document.createElement("a");
//       a.href = blobUrl;
//       a.download = title;
//       document.body.appendChild(a);
//       a.click();
//       document.body.removeChild(a);
//       window.URL.revokeObjectURL(blobUrl);

//       toast({
//         title: "Download successful",
//         description: "Document downloaded successfully",
//       });
//     } catch (error) {
//       console.error("Download failed:", error);
//       toast({
//         title: "Error",
//         description: "Failed to download, please try again later",
//       });
//     }
//   };

//   return (
//     <div className="space-y-4 p-4 border rounded-lg shadow-md ">
//       <div className="flex justify-between items-center">
//         <h2 className="text-lg font-semibold text-muted-foreground">
//           DocumentList
//         </h2>
//         <Button variant="outline" onClick={() => setIsOpen(!isOpen)}>
//           {isOpen ? "Hide DocumentList" : "Show DocumentList"}
//           {isOpen ? (
//             <ChevronUp className="ml-2" />
//           ) : (
//             <ChevronDown className="ml-2" />
//           )}
//         </Button>
//       </div>
//       {isOpen && (
//         <div className="flex flex-col gap-3 mt-2">
//           {documentList.length > 0 ? (
//             documentList.map(({ id, title, download_url }) => (
//               <div
//                 key={id}
//                 className="flex justify-between items-center p-3 border rounded-md transition"
//               >
//                 <p className="text-sm truncate max-w-[70%]" title={title}>
//                   {title}
//                 </p>
//                 <Button
//                   variant="outline"
//                   onClick={() => handleDownload(download_url, title)}
//                 >
//                   <Download />
//                 </Button>
//               </div>
//             ))
//           ) : (
//             <p className="text-sm text-gray-500">No documentList available.</p>
//           )}
//         </div>
//       )}
//     </div>
//   );
// }
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import axios from "axios";
import { Download, Trash2, ChevronDown, ChevronUp } from "lucide-react";
import { useRecoilState } from "recoil";
import { documentIdsState, loaderState } from "@/store/chat";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

interface Document {
  id: number;
  title: string;
  download_url: string;
}

export default function DocumentList() {
  const [documents, setDocuments] = useRecoilState<string[]>(documentIdsState);
  const [documentList, setDocumentList] = useState<Document[]>([]);
  const [loader, setLoader] = useRecoilState(loaderState);
  const [isOpen, setIsOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const { toast } = useToast();
  const url = import.meta.env.VITE_API_URL;

  const fetchDocuments = async () => {
    try {
      const token = localStorage.getItem("token");
      console.log("Fetching documents...");
      const response = await axios.get(`${url}/api/documents`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });
      setDocuments(response.data.documents);
    } catch (error) {
      console.error("Error fetching documents:", error);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [documentList]);

  useEffect(() => {
    if (isOpen) {
      fetchDocumentList();
    }
  }, [isOpen, loader]);

  const fetchDocumentList = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${url}/api/documents/list/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await response.json();
      setDocumentList(data.documents);
    } catch (error) {
      console.error("Failed to fetch documentList:", error);
    }
  };

  const handleDownload = async (downloadUrl: string, title: string) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${url}${downloadUrl}`, {
        method: "GET",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) {
        toast({
          title: "Error",
          description: "Failed to download, please try again later",
        });
        return;
      }

      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = blobUrl;
      a.download = title;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(blobUrl);

      toast({
        title: "Download successful",
        description: "Document downloaded successfully",
      });
    } catch (error) {
      console.error("Download failed:", error);
      toast({
        title: "Error",
        description: "Failed to download, please try again later",
      });
    }
  };

  const handleDelete = async (documentId: number) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(
        `${url}/api/documents/${documentId}/delete/`,
        {
          method: "DELETE",
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (!response.ok) {
        toast({ title: "Error", description: "Failed to delete document" });
        return;
      }

      setDocumentList(documentList.filter((doc) => doc.id !== documentId));
      toast({ title: "Deleted", description: "Document deleted successfully" });
    } catch (error) {
      console.error("Delete failed:", error);
      toast({ title: "Error", description: "Failed to delete document" });
    }
  };

  return (
    <div className="space-y-4 p-4 border rounded-lg shadow-md ">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold text-muted-foreground">
          Documents
        </h2>
        <Button variant="outline" onClick={() => setIsOpen(!isOpen)}>
          {isOpen ? "Hide Documents" : "Show Documents"}
          {isOpen ? (
            <ChevronUp className="ml-2" />
          ) : (
            <ChevronDown className="ml-2" />
          )}
        </Button>
      </div>
      {isOpen && (
        <div className="flex flex-col gap-3 mt-2">
          {documentList?.length > 0 ? (
            documentList.map(({ id, title, download_url }) => (
              <div
                key={id}
                className="flex justify-between items-center p-3 border rounded-md transition"
              >
                <p className="text-sm truncate max-w-[60%]" title={title}>
                  {title}
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => handleDownload(download_url, title)}
                  >
                    <Download />
                  </Button>
                  <Dialog
                    open={deleteId === id}
                    onOpenChange={(open) => setDeleteId(open ? id : null)}
                  >
                    <DialogTrigger asChild>
                      <Button
                        variant="outline"
                        className="text-red-500 hover:text-red-600"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <Trash2 />
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-[425px] rounded-lg shadow-lg">
                      <DialogHeader>
                        <DialogTitle className="text-lg font-semibold text-primary">
                          Delete Document
                        </DialogTitle>
                        <DialogDescription className="text-sm text-gray-500">
                          Are you sure you want to delete "{title}"? This action
                          cannot be undone.
                        </DialogDescription>
                      </DialogHeader>
                      <DialogFooter className="mt-4">
                        <Button
                          variant="outline"
                          onClick={() => setDeleteId(null)}
                        >
                          Cancel
                        </Button>
                        <Button
                          variant="destructive"
                          onClick={() => handleDelete(id)}
                        >
                          Delete
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                </div>
              </div>
            ))
          ) : (
            <p className="text-sm text-gray-500">No documents available.</p>
          )}
        </div>
      )}
    </div>
  );
}
