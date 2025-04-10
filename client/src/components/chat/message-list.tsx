import { useCallback, useEffect, useRef, useState } from "react";
import { useRecoilState, useRecoilValue } from "recoil";
import { loaderState, messagesState, selectedConversationIdState } from "@/store/chat";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar } from "@/components/ui/avatar";
import { Bot, User, ArrowDown, Loader } from "lucide-react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";

const SleekProgressBar = ({ progress }: { progress: number }) => {
  // Ensure progress is between 0-100
  const normalizedProgress = Math.min(100, Math.max(0, progress));
  
  return (
    <div className="flex items-center ml-2 gap-2">
      <div className="relative h-2 w-20 bg-muted rounded-full overflow-hidden">
        <div 
          className="absolute top-0 left-0 h-full bg-primary rounded-full transition-all duration-300 ease-out"
          style={{ width: `${normalizedProgress}%` }}
        />
      </div>
      <span className="text-xs font-medium text-muted-foreground">{Math.round(normalizedProgress)}%</span>
    </div>
  );
};

const MessageItem = ({ message, index, isLast }: { message: { role: string; content: string; type?: string }; index: number; isLast: boolean }) => {
  const isAssistantMessage = message.role === "assistant";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      className={`flex gap-3 ${isAssistantMessage ? "bg-muted/50 p-4 rounded-lg" : ""}`}
    >
      <Avatar className="h-8 w-8">
        {isAssistantMessage ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
      </Avatar>
      <motion.div
        className="flex-1"
        initial={{ scale: 0.95 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.2 }}
      >
        {message.type === "document_added" ? (
          <p style={{ whiteSpace: "pre-wrap" }} className="text-sm leading-relaxed">📄 {message.content}</p>
        ) : (
          <p style={{ whiteSpace: "pre-wrap" }} className="text-sm leading-relaxed">{message.content}</p>
        )}
      </motion.div>
    </motion.div>
  );
};

export default function MessageList() {
  const [messages, setMessages] = useRecoilState(messagesState);
  const [loader, setLoader] = useRecoilState(loaderState);
  const scrollRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [selectedConversationId, setSelectedConversationId] = useRecoilState(selectedConversationIdState);
  const url = import.meta.env.VITE_API_URL;

  // Scroll to bottom function
  const scrollToBottom = () => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
    setShowScrollButton(false);
  };

  const fetchMessages = async () => {
    if (!selectedConversationId) return;

    try {
      console.log("🚀 Fetching messages for:", selectedConversationId);

      const token = localStorage.getItem("token");

      const response = await fetch(`${url}/api/conversations/${selectedConversationId}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : "",
        },
      });

      const data = await response.json();

      if (data.conversation?.timeline) {
        const formattedMessages = data.conversation.timeline
          .filter((item: any) => item.type === "message")
          .map((msg: any) => ({
            role: msg.role,
            content: msg.content,
          }));
        setMessages(formattedMessages);
      }
    } catch (error) {
      console.error("Error fetching messages:", error);
    }
  };

  useEffect(() => {
    if (selectedConversationId) {
      fetchMessages();
    } else {
      setMessages([]);
    }
  }, [selectedConversationId]);

  // Detect if the user is at the bottom
  const handleScroll = () => {
    if (!containerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    setShowScrollButton(scrollTop + clientHeight < scrollHeight - 50);
  };

  // Auto-scroll when new messages arrive (unless user manually scrolled up)
  useEffect(() => {
    if (!showScrollButton) scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const chatContainer = containerRef.current;
    if (chatContainer) {
      chatContainer.addEventListener("scroll", handleScroll);
      return () => chatContainer.removeEventListener("scroll", handleScroll);
    }
  }, []);

  return (
    <div className="relative">
      <ScrollArea ref={containerRef} className="min-h-[200px] pr-4 overflow-y-auto max-h-[60vh]">
        <div className="space-y-4 flex-1">
          {messages.map((message, i) => (
            <MessageItem key={i} message={message} index={i} isLast={i === messages.length - 1} />
          ))}

          {loader.processing && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="flex gap-3 bg-muted/50 p-4 rounded-lg"
            >
              <Avatar className="h-8 w-8">
                <Bot className="h-4 w-4" />
              </Avatar>
              <div className="flex items-center">
                <span className="text-sm text-muted-foreground">{loader?.document || "Processing..."}</span>
                <SleekProgressBar progress={loader?.progress || 0} />
              </div>
            </motion.div>
          )}
          <div ref={scrollRef} /> {/* Invisible element for auto-scroll */}
        </div>
      </ScrollArea>

      {/* Scroll to bottom button */}
      {showScrollButton && (
        <Button
          onClick={scrollToBottom}
          className="fixed bottom-4 right-4 p-2 bg-gray-800 text-white rounded-full shadow-lg"
        >
          <ArrowDown className="w-5 h-5" />
        </Button>
      )}
    </div>
  );
}