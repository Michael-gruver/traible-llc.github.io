import { z } from "zod";

export const userSchema = z.object({
  id: z.number(),
  username: z.string(),
  email: z.string().email(),
});

export type User = z.infer<typeof userSchema>;

export const mockUser: User = {
  id: 1,
  username: "demo_user",
  email: "demo@example.com",
};
export interface Message {
  role: "user" | "assistant";
  content: string;
}
export interface Conversation {
  id: string;
  title: string;
  created_at: string;
}