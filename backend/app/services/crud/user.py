"""
User CRUD operations.
"""
from typing import Optional, List
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserRoleUpdate
from app.core.security import get_password_hash


async def get_user(db: AsyncSession, user_id: str) -> Optional[User]:
    """Get user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_users(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    role: Optional[str] = None,
    is_active: Optional[bool] = None
) -> List[User]:
    """Get list of users with optional filtering"""
    query = select(User)
    
    if role:
        query = query.where(User.role == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """Create a new user"""
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=UserRole.CANDIDATE.value,
        is_verified=False
    )
    db.add(user)
    await db.flush()
    return user


async def update_user(db: AsyncSession, user: User, user_data: UserUpdate) -> User:
    """Update user profile"""
    update_dict = user_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(user, field, value)
    await db.flush()
    return user


async def update_user_role(db: AsyncSession, user: User, role_data: UserRoleUpdate) -> User:
    """Update user role (admin only)"""
    user.role = role_data.role
    await db.flush()
    return user


async def update_user_password(db: AsyncSession, user: User, new_password: str) -> User:
    """Update user password"""
    user.password_hash = get_password_hash(new_password)
    await db.flush()
    return user


async def verify_user(db: AsyncSession, user: User) -> User:
    """Mark user as verified"""
    user.is_verified = True
    await db.flush()
    return user


async def deactivate_user(db: AsyncSession, user: User) -> User:
    """Deactivate user account"""
    user.is_active = False
    await db.flush()
    return user


async def activate_user(db: AsyncSession, user: User) -> User:
    """Activate user account"""
    user.is_active = True
    await db.flush()
    return user


async def delete_user(db: AsyncSession, user: User) -> None:
    """Delete user permanently"""
    await db.delete(user)
    await db.flush()


async def search_users(db: AsyncSession, query: str, limit: int = 20) -> List[User]:
    """Search users by email or name"""
    search_pattern = f"%{query}%"
    result = await db.execute(
        select(User)
        .where(
            or_(
                User.email.ilike(search_pattern),
                User.first_name.ilike(search_pattern),
                User.last_name.ilike(search_pattern)
            )
        )
        .limit(limit)
    )
    return list(result.scalars().all())


async def count_users(db: AsyncSession, role: Optional[str] = None) -> int:
    """Count total users"""
    from sqlalchemy import func
    query = select(func.count(User.id))
    if role:
        query = query.where(User.role == role)
    result = await db.execute(query)
    return result.scalar() or 0
