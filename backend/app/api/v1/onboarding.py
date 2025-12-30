from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.onboarding import OnboardingRequest, OnboardingCurriculum
from app.services.onboarding_service import generate_curriculum

router = APIRouter()


@router.post("/generate", response_model=OnboardingCurriculum)
async def generate_onboarding_curriculum(
    payload: OnboardingRequest,
    current_user: str = Depends(get_current_user),
) -> OnboardingCurriculum:
    """Generate a 30-day onboarding curriculum for a given role/context."""

    curriculum = await generate_curriculum(payload, requested_by=current_user)
    return curriculum
