from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from ...core.config import settings
from ...core.utils.ai_core.chains import PydancticLLMChain
from ..models import Chat

SYSTEM_PROMPT = """
You are an AI assistant designed to help users with their inquiries through a conversational interface. Your primary goal is to understand the user's needs, existing knowledge about the topic, and the desired outcome they want to achieve. To do this effectively, you will ask a series of clarifying questions before providing any solutions or recommendations.

When interacting with users, follow these guidelines:
1. Greet the user warmly and introduce yourself as an AI assistant.
2. Ask open-ended questions to gather information about the user's needs and goals.
3. Inquire about the user's existing knowledge on the topic to tailor your responses accordingly.
4. Clarify any ambiguous statements by asking follow-up questions.
5. Summarize the information gathered to ensure you have a clear understanding of the user's requirements.
6. Once you have sufficient information, provide well-informed solutions or recommendations that align with the user's goals.
7. Maintain a friendly and professional tone throughout the conversation.

Termination Criteria:
- The conversation should conclude when the user indicates that they have received satisfactory assistance or when all their questions have been answered.
- If 10 consecutive exchanges occur without significant progress toward understanding the user's needs, politely suggest concluding the session.

Remember, your role is to assist the user by first understanding their needs through thoughtful questioning before offering any solutions.
You must ASK ONLY ONE QUESTION at a time and wait for the user's response before asking the next question.

You will receive user question, answer, chat_history, session_id as input variables.
"""


class ChatTitleSchema(BaseModel):
    title: str = Field(..., description="The generated title for the chat")


class ChatHistoryItemSchema(BaseModel):
    question: str = Field(..., description="The user's question")
    answer: str = Field(..., description="The assistant's answer")
    order: int = Field(
        ..., description="The order of the interaction in the chat history"
    )


class UserQuerySchema(BaseModel):
    question: Optional[str] = Field(
        None, description="The clarifying question generated for the user"
    )
    completed: Optional[bool] = Field(
        False, description="Indicates if no further questions are needed"
    )


class AIService:
    @staticmethod
    async def get_chat_title(initial_message: str) -> str:
        prompt_template = """
        Given the user's initial message: "{initial_message}", generate a concise and relevant title for the chat session that reflects the main topic or purpose of the conversation.
        {format_instructions}
        Title:
        """

        chain = PydancticLLMChain(
            pydantic_model=ChatTitleSchema,
            prompt_template=prompt_template,
            input_variables=[{"name": "initial_message", "type": "str"}],
            model_name=settings.openai_model_name,
            api_key=settings.openai_api_key,
            temperature=0.5,
        )

        result = await chain.arun({"initial_message": initial_message})
        return result["title"]

    async def generate_clarifying_question(
        self,
        user_message: str,
        chat_history: list[ChatHistoryItemSchema],
        session_id: str,
    ) -> str | None:
        prompt_template = (
            SYSTEM_PROMPT
            + """
        Chat History:
        {chat_history}

        User Message:
        {user_message}
        {format_instructions}
        Based on the above chat history and user message, generate a single clarifying question to better understand the user's needs.
        """
        )

        chain = PydancticLLMChain(
            pydantic_model=UserQuerySchema,
            prompt_template=prompt_template,
            input_variables=[
                {"name": "chat_history", "type": "list"},
                {"name": "user_message", "type": "str"},
                {"name": "session_id", "type": "str"},
            ],
            model_name=settings.openai_model_name,
            api_key=settings.openai_api_key,
            temperature=0.7,
        )

        result = await chain.arun(
            {
                "chat_history": chat_history,
                "user_message": user_message,
                "session_id": session_id,
            }
        )
        return result["question"] if not result["completed"] else None
