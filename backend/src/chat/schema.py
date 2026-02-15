from datetime import datetime
from enum import Enum
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
    question_type: Optional[str] = Field(
        None, description="The type of the question (e.g., 'text', 'multiple_choice')"
    )
    options: Optional[List[str]] = Field(
        None, description="Optional list of predefined answer options for the question"
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


class ChatTitleSchema(BaseModel):
    title: str = Field(..., description="The generated title for the chat")


class ChatHistoryItemSchema(BaseModel):
    question: str = Field(..., description="The user's question")
    answer: str = Field(..., description="The assistant's answer")
    order: int = Field(
        ..., description="The order of the interaction in the chat history"
    )
    question_type: Optional[str] = Field(
        None, description="The type of the question (e.g., 'text', 'multiple_choice')"
    )
    options: Optional[List[str]] = Field(
        None, description="Optional list of predefined answer options for the question"
    )


class QuestionType(str, Enum):
    TEXT = "text"
    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_CHOICE = "single_choice"


class QuestionnaireQuestionSchema(BaseModel):
    order: int = Field(..., description="Order of the question in the questionnaire")
    question: str = Field(..., description="The clarifying question to ask the user")
    options: Optional[List[str]] = Field(
        None, description="Optional list of predefined answer options for the question"
    )
    question_type: Optional[QuestionType] = Field(
        None,
        description="Type of the question (e.g., 'text', 'multiple_choice', 'single_choice')",
    )
    completed: bool = Field(
        False,
        description=(
            "Indicates whether the questionnaire is completed. If true, the "
            "AI has finished asking questions."
        ),
    )


class ChatInteractionResponse(BaseModel):
    """Response payload for a single chat interaction.

    - "session_id" is always the chat.id in the database.
    - "question" is the next clarifying question from the AI, or null
      if no further questions are needed.
    - "completed" indicates that the AI has finished asking questions.
    """

    session_id: UUID = Field(..., description="Chat session identifier (chat.id)")
    order: Optional[int] = Field(
        ..., description="Order of the question in the questionnaire"
    )
    question: Optional[str] = Field(
        ..., description="The clarifying question to ask the user"
    )
    options: Optional[List[str]] = Field(
        None, description="Optional list of predefined answer options for the question"
    )
    question_type: Optional[QuestionType] = Field(
        None,
        description="Type of the question (e.g., 'text', 'multiple_choice', 'single_choice')",
    )
    completed: bool = Field(
        False,
        description=(
            "Indicates whether the questionnaire is completed. If true, the "
            "AI has finished asking questions."
        ),
    )


class ChatHistoryResponse(BaseModel):
    """Full chat history for a given session.

    Exposes the ordered list of clarifying question/answer turns so the
    frontend can render the entire conversation.
    """

    session_id: UUID = Field(..., description="Chat session identifier (chat.id)")
    title: str = Field(..., description="Title of the chat")
    status: ChatStatus = Field(..., description="Current status of the chat")
    history: List[ChatHistoryItemSchema] = Field(
        default_factory=list,
        description="Ordered chat turns with question and answer",
    )


class GenerateRoadmapResponse(BaseModel):
    """Response returned when roadmap generation is triggered."""

    session_id: UUID = Field(..., description="Chat session identifier")
    status: str = Field(
        ...,
        description="Current status of roadmap generation (pending, in_progress, completed, error)",
    )
    message: str = Field(
        ..., description="Human-readable message about the generation status"
    )
