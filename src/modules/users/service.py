from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.modules.users.models import User


async def create_user(
        session: AsyncSession,
        username: str,
        email: str,
        hashed_password: str
) -> Optional[User]:
    try:
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        print(f"✓ Пользователь создан: {user.username}")
        return user
    except Exception as e:
        await session.rollback()
        print(f"✗ Ошибка: {e}")
        return None


async def get_all_users(session: AsyncSession) -> List[User]:
    result = await session.execute(select(User))
    return list(result.scalars().all())


async def get_user_by_id(
        session: AsyncSession,
        user_id: int
) -> Optional[User]:
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_username(
        session: AsyncSession,
        username: str
) -> Optional[User]:
    result = await session.execute(
        select(User).where(User.username == username)
    )
    return result.scalar_one_or_none()


async def update_user(
        session: AsyncSession,
        user_id: int,
        **kwargs
) -> Optional[User]:

    user = await get_user_by_id(session, user_id)
    if not user:
        return None

    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)

    await session.commit()
    await session.refresh(user)
    return user


async def delete_user(
        session: AsyncSession,
        user_id: int
) -> bool:
    user = await get_user_by_id(session, user_id)
    if not user:
        return False

    await session.delete(user)
    await session.commit()
    return True