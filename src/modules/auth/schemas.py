from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserRegister(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=63,
        description="Уникальное имя пользователя"
    )
    email: EmailStr = Field(
        ...,
        description="Email адрес"
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="Пароль (минимум 6 символов)"
    )
    password_confirm: str = Field(
        ...,
        description="Подтверждение пароля"
    )

    @field_validator('username')
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username может содержать только буквы, цифры и _')
        return v.lower()

    @field_validator('password_confirm')
    def passwords_match(cls, v: str, info) -> str:
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Пароли не совпадают')
        return v


class UserLogin(BaseModel):
    login: str = Field(
        ...,
        description="Username или email"
    )
    password: str = Field(
        ...,
        description="Пароль"
    )


class UserInfo(BaseModel):
    id: int = Field(..., description="ID пользователя")
    username: str = Field(..., description="Имя пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    is_active: bool = Field(default=True, description="Активен ли пользователь")

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    message: str = "Successfully logged in"
    user: UserInfo