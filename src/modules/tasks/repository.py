from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.tasks.models import Task

async def save(session: AsyncSession, task: Task) -> Task:
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

async def get_all_by_owner(session: AsyncSession, owner_id: int) -> List[Task]:
    result = await session.execute(select(Task).where(Task.owner_id == owner_id))
    return list(result.scalars().all())

async def get_by_id(session: AsyncSession, task_id: int) -> Optional[Task]:
    return await session.get(Task, task_id)

async def delete(session: AsyncSession, task: Task) -> None:
    await session.delete(task)
    await session.commit()