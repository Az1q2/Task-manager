from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import hash_password, verify_password
from src.modules.users.models import User
from src.modules.users import repository as user_repository
from src.modules.auth.schemas import UserRegister, UserLogin


class AuthError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


async def register_user(session: AsyncSession, user_data: UserRegister) -> User:
    if await user_repository.get_by_username(session, user_data.username):
        raise AuthError("Пользователь с таким username уже существует")
    if await user_repository.get_by_email(session, user_data.email):
        raise AuthError("Этот email уже зарегистрирован")

    hashed_pw = hash_password(user_data.password)

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pw,
        is_active=True
    )
    return await user_repository.save(session, new_user)


async def authenticate_user(session: AsyncSession, login_data: UserLogin) -> User:
    user = await user_repository.get_by_username(session, login_data.login)
    if not user:
        user = await user_repository.get_by_email(session, login_data.login)

    if not user:
        raise AuthError("Неверный логин или пароль")

    try:
        password_verified = verify_password(login_data.password, user.hashed_password)
    except (ValueError, TypeError):
        raise AuthError("Неверный логин или пароль")

    if not password_verified:
        raise AuthError("Неверный логин или пароль")

    return user