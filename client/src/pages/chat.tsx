import { useEffect } from "react";
import { useLocation } from "wouter";
import { useRecoilValue } from "recoil";
import { isAuthenticatedState } from "@/store/auth";
import ChatInterface from "@/components/chat/chat-interface";
import DocumentList from "@/components/chat/chat-documentList";
import PdfUpload from "@/components/pdf/pdf-upload";
import ConversationList from "@/components/chat/ConversationList";
import MessageList from "@/components/chat/message-list";
import { useNavigate } from "react-router-dom";

export default function Chat() {
  const isAuthenticated = useRecoilValue(isAuthenticatedState);
const navigate = useNavigate()

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/auth");
    }
  }, [isAuthenticated]);

  if (!isAuthenticated) return null;
  

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-2 space-y-6 h-[75vh] flex flex-col justify-between">
          <PdfUpload />
          <MessageList />
          <ChatInterface />
        </div>
        <div className="space-y-6 mt-[50px] md:mt-0 md:overflow-y-auto md:max-h-[78vh]">
          <DocumentList />
          <ConversationList />
        </div>
      </div>
    </div>
  );
}
