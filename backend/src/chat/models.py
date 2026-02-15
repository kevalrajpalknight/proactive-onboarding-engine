import enum

from sqlalchemy import JSON, UUID, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..core.database import Base
from ..core.models import TimeStampMixin, UUIDMixin


class ChatStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"


class Chat(Base, UUIDMixin, TimeStampMixin):
    __tablename__ = "chats"

    title = Column(String(255), nullable=False)
    status = Column(Enum(ChatStatus), default=ChatStatus.ACTIVE)
    initial_message = Column(String(1000), nullable=True)
    question_answers = Column(JSON, nullable=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    token_consumed = Column(Integer, default=0)
    model_used = Column(String(100), nullable=True)
    chat_metadata = Column(JSON, nullable=True)

    user = relationship("User", back_populates="chats")

    def __repr__(self) -> str:
        return f"<Chat id={self.id} title={self.title} status={self.status}>"
