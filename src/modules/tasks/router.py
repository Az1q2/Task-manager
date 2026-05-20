from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.dependencies import get_db
from src.modules.auth.dependencies import get_current_user
from src.modules.users.models import User
from src.modules.tasks.schemas import TaskCreate, TaskUpdate, TaskResponse
# Импортируем модуль
from src.modules.tasks import service as task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_new_task(
        task_in: TaskCreate,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
):
    task = await task_service.create_task(
        session=session,
        title=task_in.title,
        owner_id=current_user.id,
        description=task_in.description
    )
    if not task:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Не удалось создать задачу")
    return task

@router.get("/", response_model=List[TaskResponse])
async def read_my_tasks(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
):
    return await task_service.get_tasks_by_owner(session, current_user.id)

@router.patch("/{task_id}", response_model=TaskResponse)
async def update_existing_task(
        task_id: int,
        task_in: TaskUpdate,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
):
    updated_task = await task_service.update_task(
        session=session,
        task_id=task_id,
        user_id=current_user.id,
        **task_in.model_dump(exclude_unset=True)
    )

    if not updated_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

    return updated_task

@router.post("/{task_id}/toggle", response_model=TaskResponse)
async def toggle_status(
        task_id: int,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
):
    task = await task_service.toggle_task_completion(session, task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_task(
        task_id: int,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
):
    success = await task_service.delete_task(session, task_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

    return Response(status_code=status.HTTP_204_NO_CONTENT)