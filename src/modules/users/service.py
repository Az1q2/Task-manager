from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.users.models import User
from src.modules.users import repository
from src.core.security import hash_password


async def create_user(session: AsyncSession, username: str, email: str, raw_password: str) -> Optional[User]:
    hashed_pw = hash_password(raw_password)
    return await repository.save_new_user(session, username, email, hashed_pw)


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    return await repository.get_by_email(session, email)


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    return await repository.get_by_id(session, user_id)


async def delete_user_by_id(session: AsyncSession, user_id: int) -> bool:
    return await repository.delete_by_id(session, user_id)