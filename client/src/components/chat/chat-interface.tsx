import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2, Send, XCircle } from "lucide-react";
import { useRecoilState, useRecoilValue } from "recoil";
import {
  conversationsState,
  documentIdsState,
  documentIdState,
  loaderState,
  messagesState,
  selectedConversationIdState,
} from "@/store/chat";
import axios from "axios";
import { Message } from "@shared/schema";

const SUGGESTED_QUESTIONS = [
  "What is this document about?",
  "Give a brief summary of the document?",
  "Explain the key points in this document.",
  "What are the main takeaways?",
];

export default function ChatInterface() {
  const [input, setInput] = useState("");
  const [loader, setLoader] = useRecoilState(loaderState);
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useRecoilState(messagesState);
  const documentId = useRecoilValue(documentIdState);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [selectedConversationId, setSelectedConversationId] = useRecoilState(
    selectedConversationIdState
  );
    const [conversations, setConversations] = useRecoilState(conversationsState);
  const abortControllerRef = useRef<AbortController | null>(null);
  const [documents, setDocuments] = useRecoilState<string[]>(documentIdsState);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [suggestedQuestions, setSuggestedQuestions] =
    useState<string[]>(SUGGESTED_QUESTIONS);

  const token = localStorage.getItem("token");
  const url = import.meta.env.VITE_API_URL;

  const fetchDocuments = async () => {
    try {
      setErrorMessage(null);
      console.log("Fetching documents...");
      const response = await axios.get(`${url}/api/documents`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      console.log("MY DOCS", response.data.documents);
      setDocuments(response.data.documents);
    } catch (error) {
      console.error("Error fetching documents:", error);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  useEffect(() => {
    if (loader.documentId) {
      setDocuments((prevDocs: any) => {
        const exists = prevDocs.some(
          (doc: any) => doc === String(loader.documentId)
        );

        if (!exists) {
          const newDocument = {
            id: loader.documentId,
            title: `Document_${loader.documentId}.pdf`,
            is_processed: false,
            created_at: new Date().toISOString(),
            content_type: "application/pdf",
          };

          return [...prevDocs, newDocument];
        }
        return prevDocs;
      });
    }
  }, [loader.documentId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !documentId) return;

    // Clear previous error message
    setErrorMessage(null);

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    setShowSuggestions(false);

    // Create a new AbortController
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch(`${url}/api/chat/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: input,
          document_ids: documents?.map((doc: any) => `${doc?.id}`),
          conversation_id: selectedConversationId,
          stream: true,
        }),
        signal: abortControllerRef.current.signal,
      });

      // Handle non-200 status codes
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.message || "An error occurred while processing the request"
        );
      }

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = "";

      // Append a new message placeholder before streaming starts
      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      while (true) {
        const { value, done } = await reader.read();

        if (done) break;

        const chunk = decoder.decode(value, { stream: true });

        // Split the stream by newlines and clean up
        const lines = chunk
          .split("\n")
          .map((line) => line.replace(/^data: /, "").trim())
          .filter((line) => line);

        for (const line of lines) {
          try {
            const parsed = JSON.parse(line);
            if (parsed.type === "chunk" && parsed.text) {
              assistantMessage += parsed.text;

              // Maintain proper spacing while updating state
              setMessages((prev) => {
                const lastMessage = prev[prev.length - 1];
                if (lastMessage.role === "assistant") {
                  return [
                    ...prev.slice(0, -1),
                    { role: "assistant", content: assistantMessage },
                  ];
                }
                return prev;
              });
            }
          } catch (err) {
            console.error("JSON parse error:", err);
          }
        }


      }

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
      fetchConversations();
    } catch (error: any) {
      console.error("🚀 ~ handleSubmit ~ error:", error);

      // Set specific error message
      const errorMsg =
        error.message || "Sorry, something went wrong. Please try again.";
      setErrorMessage(errorMsg);

      if (error.name === "AbortError") {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: "Request was cancelled." },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: errorMsg,
          },
        ]);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleStopRequest = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort(); // Abort API request
      setLoading(false);
    }
  };

  const handleSuggestedQuestion = (question: string) => {
    setInput(question);

    // Remove only the clicked question from the suggested questions
    setSuggestedQuestions((prevQuestions) =>
      prevQuestions.filter((q) => q !== question)
    );

    // Hide suggestions if no questions remain
    if (suggestedQuestions.length <= 1) {
      setShowSuggestions(false);
    }
  };

  return (
    <div className="space-y-3">
      {errorMessage && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-md">
          {errorMessage}
        </div>
      )}

      {loading && (
        <div className="text-sm text-muted-foreground flex items-center gap-2">
          <Loader2 className="w-4 h-4 animate-spin" />
          Thinking...
        </div>
      )}

      {showSuggestions && suggestedQuestions.length > 0 && (
        <div className="space-y-2">
          <h3 className="font-semibold text-sm text-muted-foreground">
            Suggested Questions
          </h3>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((question) => (
              <Button
                key={question}
                variant="outline"
                className="text-sm"
                onClick={() => handleSuggestedQuestion(question)}
              >
                {question}
              </Button>
            ))}
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex gap-2">
        <Input
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            errorMessage && setErrorMessage(null);
          }}
          placeholder="Ask questions related to your PDF..."
          className="flex-1"
          disabled={loading}
        />

        <Button
          type="submit"
          disabled={loading || !documentId || loader.processing}
        >
          {loading ? (
            <>
              {documentId} <Loader2 className="w-4 h-4 animate-spin" /> Thinking
            </>
          ) : (
            <Send className="w-4 h-4" />
          )}
        </Button>

        {loading && (
          <Button
            type="button"
            variant="destructive"
            onClick={handleStopRequest}
          >
            <XCircle className="w-4 h-4" /> Stop
          </Button>
        )}
      </form>
    </div>
  );
}
