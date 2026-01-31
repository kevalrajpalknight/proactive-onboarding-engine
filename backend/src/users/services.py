from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.jwt import create_access_token
from ..core.utils.hashing import get_password_hash, verify_password
from .models import User


class UserService:

    @staticmethod
    async def create_user(
        db_session: AsyncSession,
        full_name: str,
        email: str,
        password: str,
        profile: str | None = None,
    ) -> User:
        hashed_password = get_password_hash(password)
        new_user = User(
            full_name=full_name, email=email, password=hashed_password, profile=profile
        )
        db_session.add(new_user)
        await db_session.commit()
        await db_session.refresh(new_user)
        return new_user

    @staticmethod
    async def get_user_by_email(db_session: AsyncSession, email: str) -> User | None:
        result = await db_session.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    @staticmethod
    async def get_user_by_id(db_session: AsyncSession, user_id: int) -> User | None:
        result = await db_session.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()

    @staticmethod
    def verify_user_password(user: User, password: str) -> bool:
        return verify_password(password, str(user.password))

    @staticmethod
    async def update_last_login(db_session: AsyncSession, user: User) -> None:
        user.last_login = datetime.utcnow()
        await db_session.commit()
        await db_session.refresh(user)

    @staticmethod
    def generate_auth_token(user: User) -> str:
        token_data = {"user_id": str(user.id), "email": user.email}
        token = create_access_token(token_data)
        return token
