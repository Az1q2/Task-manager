from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.dependencies import get_db
from src.modules.auth.schemas import UserRegister, UserLogin, UserInfo, LoginResponse
from src.modules.auth import service as auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserInfo)
async def register(user_data: UserRegister, session: AsyncSession = Depends(get_db)):
    result = await auth_service.register_user(session, user_data)

    if isinstance(result, str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result)

    if not result:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Не удалось создать пользователя")

    return result

@router.post("/login", response_model=LoginResponse)
async def login(user_data: UserLogin, response: Response, session: AsyncSession = Depends(get_db)):
    user = await auth_service.authenticate_user(session, user_data)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверное имя пользователя или пароль")

    response.set_cookie(key="user_id", value=str(user.id), httponly=True)
    user_info = UserInfo.model_validate(user)
    return LoginResponse(user=user_info)

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="user_id")
    return {"message": "Successfully logged out"}