export type Sender = "user" | "bot";

// High-level semantic type of a message from the AI
export type MessageContentType = "question" | "information";

// Supported question formats for knowledge checks
export type QuestionType =
  | "single_choice"
  | "multiple_choice"
  | "open_text"
  | "date"
  | "number";

// Option metadata for choice-based questions
export interface QuestionOption {
  optionText: string;
  optionValue: string;
  orderIndex: number;
}

// Roadmap structures for a tailored course card
export type RoadmapLevel = "beginner" | "intermediate" | "advanced";

export interface RoadmapTopic {
  id: string;
  title: string;
  description?: string;
  status: "not_started" | "in_progress" | "completed";
  estimatedDuration?: string; // e.g. "30 min", "2 days"
  links?: string[]; // Optional list of resource links for the topic
}

export interface RoadmapSection {
  id: string;
  title: string;
  description?: string;
  topics: RoadmapTopic[];
}

// Course roadmap that the AI can attach as a card in chat
export interface CourseRoadmap {
  id: string;
  title: string;
  objective: string;
  description: string;
  level: RoadmapLevel;
  totalEstimatedDuration?: string;
  sections: RoadmapSection[];
}

// Chat message exchanged between user and assistant.
// The AI can optionally attach question metadata and/or
// a tailored course roadmap card to a message.
export interface Message {
  id: string;
  sender: Sender;
  text: string;
  timestamp: string;

  // Semantic payload describing how to interpret the message
  type?: MessageContentType;
  questionType?: QuestionType;
  responseRequired?: boolean;
  questionText?: string;
  options?: QuestionOption[] | null;

  // When present, this message should render as a clickable
  // course card that opens a dedicated roadmap page.
  courseRoadmap?: CourseRoadmap | null;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
}
