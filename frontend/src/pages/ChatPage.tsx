import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ChatLayout } from '../components/layout/ChatLayout'
import type { Conversation, CourseRoadmap, Message } from '../types/chat'

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
  const navigate = useNavigate()
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

      const courseRoadmap: CourseRoadmap = {
        id: `course-${Date.now()}`,
        title: 'Tailored onboarding roadmap',
        objective: 'Get you productive and confident with this project stack.',
        description:
          'Based on your answers, here is a step-by-step learning path covering architecture, tools, and workflows used in this codebase.',
        level: 'beginner',
        totalEstimatedDuration: '1-2 weeks (part-time)',
        sections: [
          {
            id: 'foundations',
            title: 'Project foundations',
            description: 'Understand the overall architecture and key services.',
            topics: [
              {
                id: 'readme-tour',
                title: 'Walk through the main README and docs',
                description: 'Identify entry points, domains, and workflows.',
                status: 'not_started',
                estimatedDuration: '30 min',
              },
              {
                id: 'backend-overview',
                title: 'Backend architecture overview',
                description: 'Review main services, modules, and dependencies.',
                status: 'in_progress',
                estimatedDuration: '1 hr',
              },
            ],
          },
          {
            id: 'hands-on',
            title: 'Hands-on workflows',
            description: 'Run the stack locally and ship a small change.',
            topics: [
              {
                id: 'run-locally',
                title: 'Run the app locally (frontend + backend)',
                status: 'completed',
                estimatedDuration: '1-2 hr',
              },
              {
                id: 'first-change',
                title: 'Implement and ship a small feature or bugfix',
                status: 'not_started',
                estimatedDuration: '2-3 hrs',
              },
            ],
          },
        ],
      }

      const botMessages: Message[] = [
        {
          id: `bot-${Date.now()}-intro`,
          sender: 'bot',
          text: simulatedReply,
          timestamp: replyTimestamp,
          type: 'information',
        },
        {
          id: `bot-${Date.now()}-course`,
          sender: 'bot',
          text: 'I have prepared a tailored onboarding course for you. Open it to see your roadmap.',
          timestamp: replyTimestamp,
          type: 'information',
          courseRoadmap,
        },
      ]

      setConversations((previous) =>
        previous.map((conversation) =>
          conversation.id === conversationId
            ? {
                ...conversation,
                messages: [...conversation.messages, ...botMessages],
              }
            : conversation,
        ),
      )

      setIsBotTyping(false)
    }, 900)
  }

  const handleOpenCourse = (course: CourseRoadmap) => {
    navigate(`/roadmap/${course.id}`, { state: { course } })
  }

  return (
    <ChatLayout
      conversations={conversations}
      activeConversationId={activeConversationId}
      onSelectConversation={handleSelectConversation}
      messages={activeConversation?.messages ?? []}
      onSendMessage={handleSendMessage}
      isBotTyping={isBotTyping}
      onOpenCourse={handleOpenCourse}
    />
  )
}
