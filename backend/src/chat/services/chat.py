import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from ..models import Chat, ChatStatus


class ChatService:
    @staticmethod
    async def create_chat(
        db_session: AsyncSession,
        title: str,
        initial_message: str,
        user_id: uuid.UUID,
        model_used: str,
        chat_id: uuid.UUID | None = None,
    ) -> Chat:
        new_chat = Chat(
            id=chat_id,
            title=title,
            initial_message=initial_message,
            user_id=user_id,
            model_used=model_used,
        )
        db_session.add(new_chat)
        await db_session.commit()
        await db_session.refresh(new_chat)
        return new_chat

    @staticmethod
    async def get_chat_by_id(
        db_session: AsyncSession, chat_id: uuid.UUID
    ) -> Chat | None:
        result = await db_session.get(Chat, chat_id)
        return result

    @staticmethod
    async def update_chat_token_consumed(
        db_session: AsyncSession, chat: Chat, tokens: int
    ) -> Chat:
        chat.token_consumed += tokens
        db_session.add(chat)
        await db_session.commit()
        await db_session.refresh(chat)
        return chat

    @staticmethod
    async def update_chat_status(
        db_session: AsyncSession, chat: Chat, status: ChatStatus
    ) -> Chat:
        chat.status = status
        db_session.add(chat)
        await db_session.commit()
        await db_session.refresh(chat)
        return chat

    @staticmethod
    async def add_question_answer(
        db_session: AsyncSession,
        chat: Chat,
        question: str,
        answer: str | None,
        question_type: str = "text",
        options: list[str] | None = None,
    ) -> Chat:
        if chat.question_answers is None:
            chat.question_answers = []
        order = len(chat.question_answers) + 1
        chat.question_answers.append(
            {
                "order": order,
                "question": question,
                "answer": answer,
                "question_type": question_type,
                "options": options,
            }
        )
        flag_modified(chat, "question_answers")
        db_session.add(chat)
        await db_session.commit()
        await db_session.refresh(chat)
        return chat

    @staticmethod
    async def get_chats_by_user_id(
        db_session: AsyncSession, user_id: uuid.UUID
    ) -> list[Chat]:
        result = await db_session.execute(select(Chat).where(Chat.user_id == user_id))
        chats = result.scalars().all()
        return chats
