from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_access_token
from app.models.auth import Token

router = APIRouter()


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    # TODO: Replace with real user validation (e.g., against company IdP or user store)
    if not form_data.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is required",
        )

    access_token = create_access_token(subject=form_data.username)
    return Token(access_token=access_token, token_type="bearer")
