import { LogOutIcon, PlusIcon } from "lucide-react";
import type { Conversation } from "../../types/chat";

interface SidebarProps {
  conversations: Conversation[];
  activeConversationId: string;
  onSelectConversation: (id: string) => void;
  onNewChat?: () => void;
  onLogout?: () => void;
}

export function Sidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
  onLogout,
}: SidebarProps) {
  return (
    <aside className="chat-sidebar">
      <div className="chat-sidebar-header">
        <div>
          <div className="chat-sidebar-title">Chats</div>
          <div className="chat-sidebar-subtitle">Previous conversations</div>
        </div>
        {onNewChat && (
          <button
            type="button"
            className="chat-sidebar-action"
            title="New chat"
            onClick={onNewChat}
          >
            <PlusIcon size={18} />
          </button>
        )}
      </div>
      <div className="chat-list">
        {conversations.map((conversation) => {
          const isActive = conversation.id === activeConversationId;
          const lastMessage =
            conversation.messages[conversation.messages.length - 1];
          return (
            <button
              key={conversation.id}
              type="button"
              className={`chat-list-item${isActive ? " chat-list-item--active" : ""}`}
              onClick={() => onSelectConversation(conversation.id)}
            >
              <div className="chat-list-item-content">
                <div className="chat-list-item-title">{conversation.title}</div>
                {lastMessage ? (
                  <div className="chat-list-item-preview">
                    {lastMessage.text}
                  </div>
                ) : (
                  <div className="chat-list-item-preview">New conversation</div>
                )}
              </div>
            </button>
          );
        })}
      </div>
      {onLogout && (
        <div className="chat-sidebar-footer">
          <button
            type="button"
            className="chat-sidebar-logout"
            onClick={onLogout}
          >
            <LogOutIcon size={16} />
            <span>Sign out</span>
          </button>
        </div>
      )}
    </aside>
  );
}
