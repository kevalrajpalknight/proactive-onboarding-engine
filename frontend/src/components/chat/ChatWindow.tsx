import type { CourseRoadmap, Message, QuestionOption } from "../../types/chat";

interface ChatWindowProps {
  messages: Message[];
  isBotTyping: boolean;
  onOpenCourse?: (course: CourseRoadmap) => void;
}

function renderQuestionOptions(options: QuestionOption[] | null | undefined) {
  if (!options || options.length === 0) return null;

  const sorted = [...options].sort((a, b) => a.orderIndex - b.orderIndex);

  return (
    <div className="chat-question-options">
      <ul>
        {sorted.map((option) => (
          <li key={option.optionValue} className="chat-question-option">
            {option.optionText}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function ChatWindow({
  messages,
  isBotTyping,
  onOpenCourse,
}: ChatWindowProps) {
  return (
    <>
      {messages.map((message) => {
        const isUser = message.sender === "user";
        return (
          <div
            key={message.id}
            className={`chat-message-row ${isUser ? "chat-message-row--user" : ""}`}
          >
            {!isUser && (
              <div className="chat-message-avatar bot" aria-hidden="true">
                <img
                  src="./src/assets/robot.png"
                  alt="AI"
                  className="chat-robot-icon"
                />
              </div>
            )}
            <div className={`chat-message-bubble ${isUser ? "user" : "bot"}`}>
              <div className="chat-message-body">
                {/* Primary text / description */}
                <div>{message.text}</div>

                {/* Render answer options for question-type messages */}
                {message.type === "question" &&
                  renderQuestionOptions(message.options)}

                {/* Tailored course card, rendered when a roadmap is attached */}
                {message.courseRoadmap && (
                  <button
                    type="button"
                    className="chat-course-card"
                    onClick={() =>
                      onOpenCourse?.(message.courseRoadmap as CourseRoadmap)
                    }
                  >
                    <div className="chat-course-card-header">
                      <div className="chat-course-card-title">
                        {message.courseRoadmap.title}
                      </div>
                      <div className="chat-course-card-level">
                        {message.courseRoadmap.level.toUpperCase()}
                      </div>
                    </div>
                    <div className="chat-course-card-body">
                      <div className="chat-course-card-objective">
                        {message.courseRoadmap.objective}
                      </div>
                      <div className="chat-course-card-description">
                        {message.courseRoadmap.description}
                      </div>
                    </div>
                    {message.courseRoadmap.totalEstimatedDuration && (
                      <div className="chat-course-card-meta">
                        Estimated duration:{" "}
                        {message.courseRoadmap.totalEstimatedDuration}
                      </div>
                    )}
                    <div className="chat-course-card-cta">
                      Open tailored roadmap
                    </div>
                  </button>
                )}
              </div>
              <div className="chat-message-meta">
                {isUser ? "You" : "Assistant"} • {message.timestamp}
              </div>
            </div>
            {isUser && (
              <div className="chat-message-avatar user" aria-hidden="true">
                You
              </div>
            )}
          </div>
        );
      })}
      {isBotTyping && (
        <div className="chat-message-row">
          <div className="chat-message-avatar bot" aria-hidden="true">
            <img
              src="./src/assets/robot.png"
              alt="AI"
              className="chat-robot-icon"
            />
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
  );
}
