from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.tasks.models import Task
from src.modules.tasks import repository


async def create_task(session: AsyncSession, title: str, owner_id: int, description: Optional[str] = None) -> Optional[
    Task]:
    task = Task(title=title, description=description, owner_id=owner_id)
    return await repository.save(session, task)


async def get_tasks_by_owner(session: AsyncSession, owner_id: int) -> List[Task]:
    return await repository.get_all_by_owner(session, owner_id)


async def get_task_by_id(session: AsyncSession, task_id: int) -> Optional[Task]:
    return await repository.get_by_id(session, task_id)


async def update_task(session: AsyncSession, task_id: int, user_id: int, **kwargs) -> Optional[Task]:
    task = await repository.get_by_id(session, task_id)
    if not task or task.owner_id != user_id:
        return None

    allowed_fields = {'title', 'description'}

    for key, value in kwargs.items():
        if key in allowed_fields and hasattr(task, key):
            setattr(task, key, value)

    return await repository.save(session, task)


async def toggle_status(session: AsyncSession, task_id: int, user_id: int) -> Optional[Task]:
    task = await repository.get_by_id(session, task_id)
    if not task or task.owner_id != user_id:
        return None

    task.is_completed = not task.is_completed
    return await repository.save(session, task)


async def delete_task(session: AsyncSession, task_id: int, user_id: int) -> bool:
    task = await repository.get_by_id(session, task_id)
    if not task or task.owner_id != user_id:
        return False
    await repository.delete(session, task)
    return True