from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.dependencies import get_db
from src.modules.auth.dependencies import get_current_user
from src.modules.users.models import User
from src.modules.users.schemas import UserResponse, UserWithTasks
from src.modules.tasks import service as task_service

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/me/tasks", response_model=UserWithTasks)
async def read_me_with_tasks(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
):
    tasks = await task_service.get_tasks_by_owner(session, current_user.id)

    return UserWithTasks(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        tasks=tasks
    )