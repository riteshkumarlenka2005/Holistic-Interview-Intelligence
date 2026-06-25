from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User

router = APIRouter()

@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Deletes all interview history, recordings, and reports for the current user.
    Account remains active.
    """
    # Assuming cascade deletes are set up on the models for `user_id` or `session_id`
    # We can delete all sessions belonging to the user.
    await db.execute(text("DELETE FROM interview_sessions WHERE user_id = :user_id"), {"user_id": current_user.id})
    await db.commit()
    return None
