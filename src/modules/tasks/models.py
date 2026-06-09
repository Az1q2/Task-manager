from sqlalchemy import String, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class Task(Base):
    __tablename__ = "tasks"

    # первичный ключ id
    id: Mapped[int] = mapped_column(primary_key=True)

    # title - указываем длину 127, делаем непустым
    title: Mapped[str] = mapped_column(String(127), nullable=False)

    # указываем тип данных текст, постгрес может хранить очень много информации в этом поле, но так же оно может быть пустым
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # булевый тип данных, по дефолту 0
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Внешний ключ, ссылающийся на id в таблице users, не может быть пустым
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Обратная связь с моделью юзер
    owner: Mapped["User"] = relationship(back_populates="tasks")