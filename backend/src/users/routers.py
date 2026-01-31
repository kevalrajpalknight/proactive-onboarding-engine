import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.dependencies import get_current_user
from ..core.database import get_db
from .models import User
from .schema import UserCreate, UserLogin, UserLoginSuccess, UserRead
from .services import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/", response_model=UserRead)
async def create_user(
    user_create: UserCreate,
    db_session: AsyncSession = Depends(get_db),
):
    existing_user = await UserService.get_user_by_email(db_session, user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    new_user = await UserService.create_user(
        db_session,
        full_name=user_create.full_name,
        email=user_create.email,
        password=user_create.password,
        profile=user_create.profile,
    )
    return new_user


@router.get("/{user_id}", response_model=UserRead)
async def read_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db),
):
    user = await UserService.get_user_by_id(db_session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.post("/login", response_model=UserLoginSuccess)
async def login_user(
    user_login: UserLogin,
    db_session: AsyncSession = Depends(get_db),
):
    user = await UserService.get_user_by_email(db_session, user_login.email)
    if not user or UserService.verify_user_password(user, user_login.password) is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    await UserService.update_last_login(db_session, user)
    token = UserService.generate_auth_token(user)
    return UserLoginSuccess(token=token, user=user)
