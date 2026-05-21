from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.dependencies import get_db
from src.modules.auth.schemas import UserRegister, UserLogin, UserInfo, LoginResponse
from src.modules.auth import service as auth_service

router = APIRouter(prefix="/api/auth", tags=["Auth API"])


@router.post("/login", response_model=LoginResponse)
async def login(user_data: UserLogin, response: Response, session: AsyncSession = Depends(get_db)):
    user = await auth_service.authenticate_user(session, user_data)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный пароль")

    response.set_cookie(key="user_id", value=str(user.id), httponly=True)
    return LoginResponse(user=UserInfo.model_validate(user))