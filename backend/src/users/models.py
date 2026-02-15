from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.orm import relationship

from ..core.database import Base
from ..core.models import TimeStampMixin, UUIDMixin


class User(Base, UUIDMixin, TimeStampMixin):
    __tablename__ = "users"

    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    profile = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)

    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} full_name={self.full_name}>"
