from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.modules.tasks.models import Task


async def create_task(
        session: AsyncSession,
        title: str,
        owner_id: int,
        description: Optional[str] = None
) -> Optional[Task]:
    try:
        task = Task(
            title=title,
            description=description,
            owner_id=owner_id
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)
        print(f"✓ Задача создана: {task.title}")
        return task
    except Exception as e:
        await session.rollback()
        print(f"✗ Ошибка: {e}")
        return None


async def get_all_tasks(session: AsyncSession) -> List[Task]:
    result = await session.execute(select(Task))
    return list(result.scalars().all())


async def get_tasks_by_owner(
        session: AsyncSession,
        owner_id: int
) -> List[Task]:
    result = await session.execute(
        select(Task).where(Task.owner_id == owner_id)
    )
    return list(result.scalars().all())


async def get_task_by_id(
        session: AsyncSession,
        task_id: int
) -> Optional[Task]:
    result = await session.execute(
        select(Task).where(Task.id == task_id)
    )
    return result.scalar_one_or_none()


async def update_task(
        session: AsyncSession,
        task_id: int,
        **kwargs
) -> Optional[Task]:
    task = await get_task_by_id(session, task_id)
    if not task:
        return None

    for key, value in kwargs.items():
        if hasattr(task, key):
            setattr(task, key, value)

    await session.commit()
    await session.refresh(task)
    return task


async def toggle_task_completion(
        session: AsyncSession,
        task_id: int
) -> Optional[Task]:
    task = await get_task_by_id(session, task_id)
    if not task:
        return None

    task.is_completed = not task.is_completed
    await session.commit()
    await session.refresh(task)
    return task


async def delete_task(
        session: AsyncSession,
        task_id: int
) -> bool:
    task = await get_task_by_id(session, task_id)
    if not task:
        return False

    await session.delete(task)
    await session.commit()
    return True