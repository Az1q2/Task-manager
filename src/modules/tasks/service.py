from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.tasks.models import Task
from src.modules.tasks import repository


class TaskError(Exception):

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class TaskNotFoundError(TaskError):
    def __init__(self):
        super().__init__("Задача не найдена")


class TaskAccessDeniedError(TaskError):
    def __init__(self):
        super().__init__("У вас нет прав на редактирование этой задачи")


async def _get_task_secure(session: AsyncSession, task_id: int, user_id: int) -> Task:
    task = await repository.get_by_id(session, task_id)
    if not task:
        raise TaskNotFoundError()
    if task.owner_id != user_id:
        raise TaskAccessDeniedError()
    return task


async def create_task(session: AsyncSession, title: str, owner_id: int, description: Optional[str] = None) -> Task:
    task = Task(title=title, description=description, owner_id=owner_id)
    return await repository.save(session, task)


async def get_tasks_by_owner(session: AsyncSession, owner_id: int) -> List[Task]:
    return await repository.get_all_by_owner(session, owner_id)


async def get_task_by_id(session: AsyncSession, task_id: int) -> Optional[Task]:
    return await repository.get_by_id(session, task_id)


async def update_task(session: AsyncSession, task_id: int, user_id: int, **kwargs) -> Task:
    task = await _get_task_secure(session, task_id, user_id)

    allowed_fields = {'title', 'description', 'is_completed'}

    for key, value in kwargs.items():
        if key in allowed_fields and hasattr(task, key):
            setattr(task, key, value)

    return await repository.save(session, task)


async def toggle_status(session: AsyncSession, task_id: int, user_id: int) -> Task:
    task = await _get_task_secure(session, task_id, user_id)
    task.is_completed = not task.is_completed
    return await repository.save(session, task)


async def delete_task(session: AsyncSession, task_id: int, user_id: int) -> None:
    task = await _get_task_secure(session, task_id, user_id)
    await repository.delete(session, task)