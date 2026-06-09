from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.users.models import User
from src.modules.users import repository
from src.core.security import hash_password

class UserError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class UserNotFoundError(UserError):
    def __init__(self):
        super().__init__("Пользователь не найден")


async def create_user(session: AsyncSession, username: str, email: str, raw_password: str) -> User:
    hashed_pw = hash_password(raw_password)
    new_user = User(username=username, email=email, hashed_password=hashed_pw)
    return await repository.save(session, new_user)


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    return await repository.get_by_email(session, email)


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    return await repository.get_by_id(session, user_id)


async def delete_user_by_id(session: AsyncSession, user_id: int) -> None:
    success = await repository.delete_by_id(session, user_id)
    if not success:
        raise UserNotFoundError()