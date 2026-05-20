from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.dependencies import get_db
from src.modules.users.models import User
from src.modules.users import service as user_service

async def get_current_user(
        user_id: str | None = Cookie(None),
        session: AsyncSession = Depends(get_db)
) -> User:
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы"
        )

    try:
        id_int = int(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный формат cookie")

    user = await user_service.get_user_by_id(session, id_int)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или заблокирован"
        )

    return user