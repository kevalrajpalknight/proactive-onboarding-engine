import type { Message } from '../../types/chat'

interface ChatWindowProps {
  messages: Message[]
  isBotTyping: boolean
}

export function ChatWindow({ messages, isBotTyping }: ChatWindowProps) {
  return (
    <>
      {messages.map((message) => {
        const isUser = message.sender === 'user'
        return (
          <div
            key={message.id}
            className={`chat-message-row ${isUser ? 'chat-message-row--user' : ''}`}
          >
            {!isUser && (
              <div className="chat-message-avatar bot" aria-hidden="true">
                <img src="./src/assets/robot.png" alt="AI" className="chat-robot-icon" />
              </div>
            )}
                <div className={`chat-message-bubble ${isUser ? 'user' : 'bot'}`}>
                  <div>{message.text}</div>
                  <div className="chat-message-meta">
                    {isUser ? 'You' : 'Assistant'}  • {message.timestamp}
                  </div>
            </div>
            {isUser && (
              <div className="chat-message-avatar user" aria-hidden="true">
                You
              </div>
            )}
          </div>
        )
      })}
      {isBotTyping && (
        <div className="chat-message-row">
          <div className="chat-message-avatar bot" aria-hidden="true">
           <img src="./src/assets/robot.png" alt="AI" className="chat-robot-icon" />
          </div>
          <div className="chat-message-bubble bot">
            <div className="chat-typing-indicator">
              <div className="chat-typing-dots" aria-hidden="true">
                <span className="chat-typing-dot" />
                <span className="chat-typing-dot" />
                <span className="chat-typing-dot" />
              </div>
                  <span className="chat-typing-label">Assistant is typing...</span>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
