import { Conversation } from '@shared/schema';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type Message = {
  role: 'user' | 'assistant';
  content: string;
};

// Mock responses for different tax-related questions
const mockResponses: Record<string, string> = {
  'What tax deductions am I eligible for?':
    'Based on common scenarios, you might be eligible for several deductions including home office expenses, charitable contributions, and retirement account contributions. However, eligibility depends on your specific situation.',
  'How do I report freelance income?':
    "Freelance income should be reported on Schedule C of Form 1040. You'll need to track all your income and expenses throughout the year. Consider making quarterly estimated tax payments to avoid penalties.",
  'When is the tax filing deadline?':
    'The standard tax filing deadline is April 15th. However, if this falls on a weekend or holiday, it may be moved to the next business day. Some taxpayers may be eligible for extensions.',
  'Can I claim home office expenses?':
    'If you use part of your home regularly and exclusively for business, you may be eligible to claim home office expenses. This can include a portion of your rent/mortgage, utilities, and maintenance costs.',
};

interface ChatState {
  conversations: Conversation[];
  documentIds: string[];
  messages: Message[];
  documentId: string[];
  conversationId: number | null;
  selectedConversationId: string;
  loader: {
    processing: boolean;
    progress: number;
    document: string;
    documentId: number;
  };
  setConversations: (conversations: Conversation[]) => void;
  setDocumentIds: (documentIds: string[] | ((prev: string[]) => string[])) => void;
  setMessages: (messages: Message[] | ((prev: Message[]) => Message[])) => void;
  addMessage: (message: Message) => void;
  setDocumentId: (documentId: string[]) => void;
  setConversationId: (conversationId: number | null) => void;
  setSelectedConversationId: (selectedConversationId: string) => void;
  setLoader: (loader: Partial<ChatState['loader']>) => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      conversations: [],
      documentIds: [],
      messages: [
        {
          role: 'assistant',
          content: "Hello! I'm your AI assistant. How can I help you today?",
        },
      ],
      documentId: [],
      conversationId: null,
      selectedConversationId: '',
      loader: {
        processing: false,
        progress: 0,
        document: '',
        documentId: 0,
      },
      setConversations: (conversations) => set({ conversations }),
      setDocumentIds: (documentIds) => set((state) => ({ 
        documentIds: typeof documentIds === 'function' ? documentIds(state.documentIds) : documentIds 
      })),
      setMessages: (messages) => set((state) => ({ 
        messages: typeof messages === 'function' ? messages(state.messages) : messages 
      })),
      addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
      setDocumentId: (documentId) => set({ documentId }),
      setConversationId: (conversationId) => set({ conversationId }),
      setSelectedConversationId: (selectedConversationId) => set({ selectedConversationId }),
      setLoader: (loader) => set((state) => ({ loader: { ...state.loader, ...loader } })),
    }),
    {
      name: 'chat-storage',
      partialize: (state) => ({
        conversations: state.conversations,
        messages: state.messages,
        selectedConversationId: state.selectedConversationId,
      }),
    }
  )
);

// Helper function to get mock response
export function getMockResponse(question: string): string {
  // Check for exact matches in mock responses
  if (mockResponses[question]) {
    return mockResponses[question];
  }

  // Default response for unmatched questions
  return 'Based on your question about taxes, I recommend consulting with a tax professional or referring to IRS guidelines for the most accurate information. Let me know if you have any other questions!';
}
