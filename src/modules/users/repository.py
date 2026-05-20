from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from src.modules.users.models import User

async def save_new_user(session: AsyncSession, username: str, email: str, hashed_pw: str) -> User:
    user = User(username=username, email=email, hashed_password=hashed_pw, is_active=True)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def get_by_email(session: AsyncSession, email: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def delete_by_id(session: AsyncSession, user_id: int) -> bool:
    stmt = delete(User).where(User.id == user_id)
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount > 0