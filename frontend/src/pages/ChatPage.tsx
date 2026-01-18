import { useMemo, useState } from 'react'
import { ChatLayout } from '../components/layout/ChatLayout'
import type { Conversation } from '../types/chat'

const initialConversations: Conversation[] = [
  {
    id: 'welcome',
    title: 'Welcome to onboarding',
    messages: [
      {
        id: 'welcome-1',
        sender: 'bot',
        text: "Hi, I'm your onboarding assistant. Ask me anything about this project, the stack, or how things work.",
        timestamp: 'Just now',
      },
    ],
  },
  {
    id: 'architecture',
    title: 'Project architecture',
    messages: [],
  },
]

export function ChatPage() {
  const [conversations, setConversations] = useState<Conversation[]>(initialConversations)
  const [activeConversationId, setActiveConversationId] = useState<string>(
    initialConversations[0]?.id ?? 'welcome',
  )
  const [isBotTyping, setIsBotTyping] = useState(false)

  const activeConversation = useMemo(
    () => conversations.find((conversation) => conversation.id === activeConversationId),
    [conversations, activeConversationId],
  )

  const handleSelectConversation = (id: string) => {
    setActiveConversationId(id)
  }

  const handleSendMessage = (text: string) => {
    if (!activeConversation) return

    const conversationId = activeConversation.id
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

    // Add user message to the active conversation
    setConversations((previous) =>
      previous.map((conversation) =>
        conversation.id === conversationId
          ? {
              ...conversation,
              messages: [
                ...conversation.messages,
                {
                  id: `user-${Date.now()}`,
                  sender: 'user',
                  text,
                  timestamp,
                },
              ],
            }
          : conversation,
      ),
    )

    // Simulate the bot typing and then responding
    setIsBotTyping(true)

    const simulatedReply =
      "Sure, I can help with that! Can you please provide more details about your existing knowledge by answering a few questions? This will help me tailor the information to your needs."

    setTimeout(() => {
      const replyTimestamp = new Date().toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
      })

      setConversations((previous) =>
        previous.map((conversation) =>
          conversation.id === conversationId
            ? {
                ...conversation,
                messages: [
                  ...conversation.messages,
                  {
                    id: `bot-${Date.now()}`,
                    sender: 'bot',
                    text: simulatedReply,
                    timestamp: replyTimestamp,
                  },
                ],
              }
            : conversation,
        ),
      )

      setIsBotTyping(false)
    }, 900)
  }

  return (
    <ChatLayout
      conversations={conversations}
      activeConversationId={activeConversationId}
      onSelectConversation={handleSelectConversation}
      messages={activeConversation?.messages ?? []}
      onSendMessage={handleSendMessage}
      isBotTyping={isBotTyping}
    />
  )
}
