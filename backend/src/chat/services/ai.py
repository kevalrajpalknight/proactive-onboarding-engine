from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from ...core.config import settings
from ...core.utils.ai_core.chains import PydancticLLMChain
from ..models import Chat
from ..schema import (
    ChatHistoryItemSchema,
    ChatTitleSchema,
    QuestionnaireQuestionSchema,
    UserQuerySchema,
)

MAX_CLARIFYING_QUESTIONS = settings.max_clarifying_questions
SYSTEM_PROMPT = """
You are an AI assistant for conversational inquiries. Your goal is to understand the user's needs, existing knowledge, and desired outcomes by asking clarifying questions.

Guidelines:
- Ask open-ended questions to gather information.
- Ask one question at a time and wait for response.
- Conclude when you have sufficient information or after {{MAX_CLARIFYING_QUESTIONS}} questions.
- Maintain a friendly, professional tone.

Remember: ASK ONLY ONE QUESTION at a time.
"""


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
    ) -> QuestionnaireQuestionSchema | None:
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
            pydantic_model=QuestionnaireQuestionSchema,
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
        return (
            QuestionnaireQuestionSchema(**result)
            if not result.get("completed")
            else None
        )
