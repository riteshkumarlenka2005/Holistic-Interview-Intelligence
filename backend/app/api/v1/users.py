"""
User management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.schemas.user import UserRead, UserUpdate
from app.services.crud import update_user as crud_update_user, delete_user as crud_delete_user

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the authenticated user's profile"""
    return current_user


@router.put("/me", response_model=UserRead)
async def update_me(
    request: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the authenticated user's profile"""
    updated = await crud_update_user(db, current_user, request)
    return updated


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete the authenticated user's account"""
    await crud_delete_user(db, current_user)
    return None
