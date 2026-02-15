import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ChatLayout } from "../components/layout/ChatLayout";
import { useAuth } from "../contexts/AuthContext";
import * as api from "../services/api";
import type { Conversation, CourseRoadmap, Message } from "../types/chat";

// ---------------------------------------------------------------------------
// Local session tracking
// ---------------------------------------------------------------------------
const SESSIONS_KEY = "poe_chat_sessions";

interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  completed: boolean;
}

function loadSessions(): ChatSession[] {
  try {
    const raw = localStorage.getItem(SESSIONS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function persistSessions(sessions: ChatSession[]) {
  // Only persist lightweight metadata – messages are reloaded from the API
  const lite = sessions.map((s) => ({
    id: s.id,
    title: s.title,
    completed: s.completed,
    messages: [] as Message[],
  }));
  localStorage.setItem(SESSIONS_KEY, JSON.stringify(lite));
}

/** Convert the backend's Q/A history into a flat list of chat messages. */
function historyToMessages(history: api.ChatHistoryItem[]): Message[] {
  const msgs: Message[] = [];
  for (const item of history) {
    msgs.push({
      id: `q-${item.order}`,
      sender: "bot",
      text: item.question,
      timestamp: "",
      type: "question",
      questionType:
        (item.question_type as Message["questionType"]) ?? undefined,
      options:
        item.options?.map((opt, idx) => ({
          optionText: opt,
          optionValue: opt,
          orderIndex: idx,
        })) ?? undefined,
    });
    if (item.answer) {
      msgs.push({
        id: `a-${item.order}`,
        sender: "user",
        text: item.answer,
        timestamp: "",
      });
    }
  }
  return msgs;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export function ChatPage() {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const [sessions, setSessions] = useState<ChatSession[]>(loadSessions);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(
    () => loadSessions()[0]?.id ?? null,
  );
  const [isBotTyping, setIsBotTyping] = useState(false);

  const activeSession = useMemo(
    () => sessions.find((s) => s.id === activeSessionId) ?? null,
    [sessions, activeSessionId],
  );

  // Persist lightweight session list whenever it changes
  useEffect(() => {
    persistSessions(sessions);
  }, [sessions]);

  // Load full history from API when switching to a session whose messages
  // haven't been fetched yet.
  useEffect(() => {
    if (!activeSession || activeSession.messages.length > 0) return;

    let cancelled = false;
    api
      .getChatHistory(activeSession.id)
      .then((res) => {
        if (cancelled) return;
        const messages = historyToMessages(res.history);
        setSessions((prev) =>
          prev.map((s) =>
            s.id === activeSession.id
              ? {
                  ...s,
                  messages,
                  title: res.title || s.title,
                  completed: res.status === "completed",
                }
              : s,
          ),
        );
      })
      .catch(() => {
        // Session might not exist on the server yet (brand-new chat)
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeSession?.id]);

  // --- handlers ---

  const handleNewChat = useCallback(() => {
    const id = crypto.randomUUID();
    const session: ChatSession = {
      id,
      title: "New conversation",
      messages: [],
      completed: false,
    };
    setSessions((prev) => [session, ...prev]);
    setActiveSessionId(id);
  }, []);

  const handleSelectConversation = useCallback((id: string) => {
    setActiveSessionId(id);
  }, []);

  const handleSendMessage = useCallback(
    async (text: string) => {
      // Auto-create a session when the user sends a message without one
      let sessionId = activeSessionId;
      if (!sessionId) {
        const id = crypto.randomUUID();
        const session: ChatSession = {
          id,
          title: "New conversation",
          messages: [],
          completed: false,
        };
        setSessions((prev) => [session, ...prev]);
        setActiveSessionId(id);
        sessionId = id;
      }

      const timestamp = new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });

      // Optimistically add user message
      const userMsg: Message = {
        id: `user-${Date.now()}`,
        sender: "user",
        text,
        timestamp,
      };

      const isFirstMessage = (activeSession?.messages.length ?? 0) === 0;

      setSessions((prev) =>
        prev.map((s) =>
          s.id === sessionId ? { ...s, messages: [...s.messages, userMsg] } : s,
        ),
      );

      setIsBotTyping(true);

      try {
        const response = await api.chatInteraction({
          session_id: sessionId,
          message: text,
        });

        const replyTs = new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        });

        const botMsg: Message = {
          id: `bot-${Date.now()}`,
          sender: "bot",
          text:
            response.question ??
            "Thank you for completing the onboarding questionnaire!",
          timestamp: replyTs,
          type: "question",
          questionType:
            (response.question_type as Message["questionType"]) ?? undefined,
          options:
            response.options?.map((opt, idx) => ({
              optionText: opt,
              optionValue: opt,
              orderIndex: idx,
            })) ?? undefined,
        };

        setSessions((prev) =>
          prev.map((s) =>
            s.id === sessionId
              ? {
                  ...s,
                  title: isFirstMessage ? text.slice(0, 60) : s.title,
                  messages: [...s.messages, botMsg],
                  completed: response.completed,
                }
              : s,
          ),
        );

        // -----------------------------------------------------------------
        // When the questionnaire is completed, trigger roadmap generation
        // and navigate to the roadmap page with a "generating" flag so
        // that the page connects via WebSocket for live progress.
        // -----------------------------------------------------------------
        if (response.completed && sessionId) {
          try {
            await api.generateRoadmap(sessionId);
          } catch {
            // Best effort — the WebSocket will still attempt to connect
          }
          navigate(`/roadmap/${sessionId}`, {
            state: { generating: true },
          });
        }
      } catch (err) {
        if (err instanceof api.ApiError && err.status === 401) {
          logout();
          navigate("/login");
          return;
        }

        const errorMsg: Message = {
          id: `error-${Date.now()}`,
          sender: "bot",
          text:
            err instanceof api.ApiError
              ? err.message
              : "Something went wrong. Please try again.",
          timestamp: new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          }),
        };

        setSessions((prev) =>
          prev.map((s) =>
            s.id === sessionId
              ? { ...s, messages: [...s.messages, errorMsg] }
              : s,
          ),
        );
      } finally {
        setIsBotTyping(false);
      }
    },
    [activeSessionId, activeSession, logout, navigate],
  );

  const handleOpenCourse = useCallback(
    (course: CourseRoadmap) => {
      navigate(`/roadmap/${course.id}`, { state: { course } });
    },
    [navigate],
  );

  // Map sessions → Conversation[] for the sidebar
  const conversations: Conversation[] = sessions.map((s) => ({
    id: s.id,
    title: s.title,
    messages: s.messages,
  }));

  return (
    <ChatLayout
      conversations={conversations}
      activeConversationId={activeSessionId ?? ""}
      onSelectConversation={handleSelectConversation}
      messages={activeSession?.messages ?? []}
      onSendMessage={handleSendMessage}
      isBotTyping={isBotTyping}
      onOpenCourse={handleOpenCourse}
      onNewChat={handleNewChat}
      onLogout={logout}
    />
  );
}
