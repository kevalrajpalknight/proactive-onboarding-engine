export type Sender = "user" | "bot";

export interface Message {
  id: string;
  sender: Sender;
  text: string;
  timestamp: string;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
}
