import type { Conversation, Message } from '../../types/chat'
import { ChatWindow } from '../chat/ChatWindow'
import { MessageInput } from '../chat/MessageInput'
import { Sidebar } from '../chat/Sidebar'

interface ChatLayoutProps {
  conversations: Conversation[]
  activeConversationId: string
  onSelectConversation: (id: string) => void
  messages: Message[]
  onSendMessage: (text: string) => void
  isBotTyping: boolean
}

export function ChatLayout({
  conversations,
  activeConversationId,
  onSelectConversation,
  messages,
  onSendMessage,
  isBotTyping,
}: ChatLayoutProps) {
  return (
    <div className="chat-app-shell">
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={onSelectConversation}
      />
      <div className="chat-main">
        <header className="chat-main-header">
          <div className="chat-main-title-block">
            <span className="chat-main-title">Proactive Onboarding Assistant</span>
            <span className="chat-main-status">
              Smart research agent to assist your onboarding
            </span>
          </div>
        </header>
        <main className="chat-main-body">
          <div className="chat-messages">
            <ChatWindow messages={messages} isBotTyping={isBotTyping} />
          </div>
        </main>
        <footer className="chat-footer">
          <MessageInput onSend={onSendMessage} isSending={isBotTyping} />
        </footer>
      </div>
    </div>
  )
}
