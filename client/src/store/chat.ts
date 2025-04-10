import { Conversation } from "@shared/schema";
import { atom } from "recoil";

export type Message = {
  role: "user" | "assistant";
  content: string;
};

// Mock responses for different tax-related questions
const mockResponses: Record<string, string> = {
  "What tax deductions am I eligible for?": "Based on common scenarios, you might be eligible for several deductions including home office expenses, charitable contributions, and retirement account contributions. However, eligibility depends on your specific situation.",
  "How do I report freelance income?": "Freelance income should be reported on Schedule C of Form 1040. You'll need to track all your income and expenses throughout the year. Consider making quarterly estimated tax payments to avoid penalties.",
  "When is the tax filing deadline?": "The standard tax filing deadline is April 15th. However, if this falls on a weekend or holiday, it may be moved to the next business day. Some taxpayers may be eligible for extensions.",
  "Can I claim home office expenses?": "If you use part of your home regularly and exclusively for business, you may be eligible to claim home office expenses. This can include a portion of your rent/mortgage, utilities, and maintenance costs.",
};
export const conversationsState = atom<Conversation[]>({
  key: "conversationsState",
  default: [],
});

export const documentIdsState = atom<string[]>({
  key: "documentIdsState",
  default: [],
});

export const messagesState = atom<Message[]>({
  key: "messages",
  default: [
    {
      role: "assistant",
      content: "Hello! I'm your AI assistant. How can I help you today?",
    },
  ],
});

// Helper function to get mock response
export function getMockResponse(question: string): string {
  // Check for exact matches in mock responses
  if (mockResponses[question]) {
    return mockResponses[question];
  }

  // Default response for unmatched questions
  return "Based on your question about taxes, I recommend consulting with a tax professional or referring to IRS guidelines for the most accurate information. Let me know if you have any other questions!";
}

export const documentIdState = atom<string[]>({
  key: "documentIdState",
  default: [],
});
export const conversationIdState = atom<number | null>({
  key: "conversationIdState",
  default: null,
});

export const selectedConversationIdState = atom<string | "">({
  key: "selectedConversationIdState",
  default: "",
});


export const loaderState = atom({
  key: 'loaderState',
  default: {
    processing: false,
    progress: 0,
    document: "",
    documentId:0,

  }
});
