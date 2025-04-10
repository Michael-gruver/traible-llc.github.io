import { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Upload } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { motion } from "framer-motion";
import axios from "axios";
import { useRecoilState, useSetRecoilState } from "recoil";
import { conversationIdState, documentIdState, loaderState } from "@/store/chat";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import TraibleLoader from "../TraibleLoader";

export default function PdfUpload() {

  const { toast } = useToast();
  const setDocumentId = useSetRecoilState(documentIdState ?? 0);
  const [conversationId, setConversationId] = useRecoilState(conversationIdState);
  const url = import.meta.env.VITE_API_URL;
  // console.log(url);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [showDialog, setShowDialog] = useState(false);
  const [loader, setLoader] = useRecoilState(loaderState);
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log("handleFileChange");
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.includes("pdf")) {
      toast({
        variant: "destructive",
        title: "Invalid file type",
        description: "Please upload a PDF file",
      });
      return;
    }

    if(selectedFile && file.name === selectedFile.name && file.size === selectedFile.size) {
      toast({
        variant: "destructive",
        title: "File already selected",
        description: "You have already selected this file",
      });
      return;
    }

    e.target.value = "";
    setSelectedFile(file);
    setShowDialog(true); // Open confirmation popup
  };
  
  const handleUpload = async () => {
    if (!selectedFile) return;
  
    const formData = new FormData();
    formData.append("file", selectedFile);
  
    const token = localStorage.getItem("token") ?? "";
    setLoader(prev => ({ ...prev, processing: true, progress: 0 })); // Start UI loader
    setShowDialog(false); // Close popup
  
    try {
      const response = await axios.post(`${url}/api/documents/upload/`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          Authorization: `Bearer ${token}`,
        },
      });
  
      const uploadedDocumentId = await response.data.document_id;
      const uploadedDocument =await response.data.title;
      setLoader(prev => ({ ...prev, documentId: uploadedDocumentId ,document: uploadedDocument})); // Store document ID
  
      toast({
        title: "Success",
        description: "PDF uploaded successfully",
      });
  
      // Poll for document processing status
      pollDocumentStatus(uploadedDocumentId, token);
    } catch (error: any) {
      setLoader(prev => ({ ...prev, processing: false })); // Stop UI loader
      toast({
        variant: "destructive",
        title: "Upload Failed",
        description: error.response?.data?.message || "Something went wrong",
      });
    }
  };
  
  const pollDocumentStatus = async (documentId: string, token: string) => {
    setLoader(prev => ({ ...prev, processing: true, progress: 0 })); // Start loader
  
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`${url}/api/documents/${documentId}/status/`, {
          headers: { Authorization: `Bearer ${token}` },
        });
  
        const { title, processing_status, processing_progress } = response.data;
  
        setLoader(prev => ({ ...prev, progress: processing_progress,document:title })); // Update progress
  
        if (processing_status === "COMPLETED" || processing_progress >= 100) {
          clearInterval(interval);
          setLoader(prev => ({ ...prev, processing: false }));
  
          toast({
            title: "Processing Complete",
            description: `Your document "${title}" is ready.`,
          });
        }
      } catch (error) {
        console.error("Error fetching document status:", error);
        clearInterval(interval);
        setLoader(prev => ({ ...prev, processing: false }));
  
        toast({
          variant: "destructive",
          title: "Error Fetching Status",
          description: "Failed to get document status.",
        });
      }
    }, 5000); // Poll every 5 seconds
  
    // Cleanup interval on unmount (optional but recommended)
    return () => clearInterval(interval);
  };
  
  
  

  return (
    <>
      {/* <motion.div
        className="flex gap-2 items-center"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Input
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          ref={fileInputRef}
          disabled={loader.processing}
        />
        <Button
          disabled={loader.processing}
          onClick={() => fileInputRef.current?.click()}
        >
          {loader.processing ? (
            <div className="flex items-center gap-2">
              <LoadingSpinner />
              <span>Uploading...</span>
            </div>
          ) : (
            <>
              <Upload className="w-4 h-4 mr-2" />
              Upload PDF
            </>
          )}
        </Button>
      </motion.div> */}

      <motion.div
        className="flex gap-2 items-center"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="relative w-full">
          <Input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            ref={fileInputRef}
            disabled={loader.processing}
            className="opacity-0 absolute w-full h-full cursor-pointer"
          />
          <div
            className="flex items-center w-full border border-input px-3 py-2 rounded-md text-sm bg-background cursor-pointer"
            onClick={() => fileInputRef.current?.click()}
          >
            {selectedFile ? selectedFile.name : "No file chosen"}
          </div>
        </div>
        <Button
          disabled={loader.processing}
          onClick={() => fileInputRef.current?.click()}
        >
          <Upload className="w-4 h-4 mr-2" />
          Upload PDF
        </Button>
      </motion.div>

      {/* ✨ Confirmation Popup */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Upload</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-gray-600">
            Are you sure you want to upload{" "}
            <strong>{selectedFile?.name}</strong>?
          </p>
          <DialogFooter>
            <Button
              variant="secondary"
              onClick={() => {
                setSelectedFile(null);
                setShowDialog(false);
              }}
            >
              Cancel
            </Button>
            <Button onClick={handleUpload} disabled={loader.processing}>
              {loader.processing ? "Uploading..." : "Confirm Upload"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}


