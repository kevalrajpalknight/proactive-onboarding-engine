from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .models import ChatStatus


class UserQuerySchema(BaseModel):
    """Request payload for a chat interaction.

    - "message" is either the initial user message (for a new chat)
      or the user's answer to the last clarifying question.
    - "session_id" is the chat id; if it does not exist yet, a new
      chat will be created with this id.
    """

    message: Optional[str] = Field(
        ...,
        description="User message for the chat agent",
    )
    session_id: Optional[UUID] = Field(
        None, description="Session ID (chat.id) to associate with the chat"
    )


class ChatTurnSchema(BaseModel):
    order: int = Field(..., description="Order of the interaction in the chat")
    question: str = Field(..., description="Clarifying question asked by the AI")
    answer: Optional[str] = Field(
        None,
        description=(
            "User's answer to the question. Will be null until the " "user responds."
        ),
    )


class ChatSchema(BaseModel):
    initial_message: Optional[str] = Field(
        None, description="The initial message of the chat"
    )
    title: str = Field(..., description="The title of the chat")
    user_id: UUID = Field(..., description="The ID of the user who owns the chat")
    model_used: str = Field(..., description="The model used for the chat")
    chat_metadata: Optional[Dict[str, str]] = Field(
        None, description="Additional metadata for the chat"
    )
    token_consumed: Optional[int] = Field(
        0, description="Number of tokens consumed in the chat"
    )
    question_answers: Optional[List[ChatTurnSchema]] = Field(
        None,
        description=(
            "Ordered list of clarifying questions and user answers " "for the chat"
        ),
    )
    status: Optional[ChatStatus] = Field(
        ChatStatus.ACTIVE,
        description="The status of the chat (active, inactive, completed)",
    )
    created_at: Optional[datetime] = Field(
        ..., description="Timestamp when the chat was created"
    )
    updated_at: Optional[datetime] = Field(
        ..., description="Timestamp when the chat was last updated"
    )


class ChatInteractionResponse(BaseModel):
    """Response payload for a single chat interaction.

    - "session_id" is always the chat.id in the database.
    - "question" is the next clarifying question from the AI, or null
      if no further questions are needed.
    - "completed" indicates that the AI has finished asking questions.
    """

    session_id: UUID = Field(..., description="Chat session identifier (chat.id)")
    question: Optional[str] = Field(
        None,
        description=(
            "Next clarifying question from the AI, or null if the " "flow is complete"
        ),
    )
    completed: bool = Field(
        ..., description="True when no further clarifying questions are needed"
    )


class ChatHistoryResponse(BaseModel):
    """Full chat history for a given session.

    Exposes the ordered list of clarifying question/answer turns so the
    frontend can render the entire conversation.
    """

    session_id: UUID = Field(..., description="Chat session identifier (chat.id)")
    title: str = Field(..., description="Title of the chat")
    status: ChatStatus = Field(..., description="Current status of the chat")
    history: List[ChatTurnSchema] = Field(
        default_factory=list,
        description="Ordered chat turns with question and answer",
    )
