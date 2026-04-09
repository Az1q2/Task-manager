from typing import List
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

class User(Base):
    __tablename__ = "users"

    # id пользователя - первичный ключ
    id: Mapped[int] = mapped_column(primary_key=True)

    # делаем username пользователя уникальным и ненулевым - тип данных стринг 2^n - 1
    username: Mapped[str] = mapped_column(String(63), unique=True, nullable=False)

    # email уникальный и ненулевой - тип данных стринг
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # захешированный ненулевой пароль - тип данных стринг
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    #булевый тип данных, по дефолту 1
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # связь один ко многим, all влияет на синхронизацию изменений, а delete-orphan на синхронизацию удаления обособленных задач
    tasks: Mapped[List["Task"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan"
    )