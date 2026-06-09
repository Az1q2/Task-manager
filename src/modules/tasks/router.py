from fastapi import APIRouter, Depends, Form, Request, Response, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.dependencies import get_db
from src.utils.templates import templates
from src.modules.auth.dependencies import get_current_user
from src.modules.users.models import User
from src.modules.tasks import service as task_service
from src.modules.tasks.service import TaskError, TaskNotFoundError, TaskAccessDeniedError
from src.modules.tasks.schemas import TaskCreate, TaskUpdate, TaskResponse
from src.modules.tasks.dependencies import get_page_user_id

router = APIRouter(tags=["Tasks"])

@router.get("/", response_class=HTMLResponse)
async def get_home_page(
        request: Request,
        search: str = None,
        session: AsyncSession = Depends(get_db)
):
    try:
        user_id = get_page_user_id(request.cookies.get("user_id"))
    except HTTPException:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    tasks = await task_service.get_tasks_by_owner(session, owner_id=user_id)

    if search:
        tasks = [task for task in tasks if search.lower() in task.title.lower()]

    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.is_completed)
    pending_tasks = total_tasks - completed_tasks

    return templates.TemplateResponse(
        request=request,
        name="tasks.html",
        context={
            "tasks": tasks,
            "total": total_tasks,
            "completed": completed_tasks,
            "pending": pending_tasks,
            "search_query": search or ""
        }
    )


@router.get("/tasks/create", response_class=HTMLResponse)
async def create_task_page(request: Request, user_id: int = Depends(get_page_user_id)):
    return templates.TemplateResponse(request=request, name="task_form.html")


@router.post("/tasks/create")
async def handle_create_task(
        title: str = Form(...),
        description: str = Form(None),
        user_id: int = Depends(get_page_user_id),
        session: AsyncSession = Depends(get_db)
):
    await task_service.create_task(session, title=title, description=description, owner_id=user_id)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/tasks/{task_id}/edit", response_class=HTMLResponse)
async def edit_task_page(
        task_id: int,
        request: Request,
        user_id: int = Depends(get_page_user_id),
        session: AsyncSession = Depends(get_db)
):
    try:
        task = await task_service.get_task_by_id(session, task_id)
        if not task or task.owner_id != user_id:
            return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

        return templates.TemplateResponse(request=request, name="task_edit.html", context={"task": task})
    except TaskError:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/tasks/{task_id}/edit")
async def handle_edit_task(
        task_id: int,
        title: str = Form(...),
        description: str = Form(None),
        user_id: int = Depends(get_page_user_id),
        session: AsyncSession = Depends(get_db)
):
    try:
        await task_service.update_task(
            session=session, task_id=task_id, user_id=user_id, title=title, description=description
        )
    except TaskError:
        pass
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/tasks/{task_id}/toggle")
async def handle_toggle_task_status(
        task_id: int,
        user_id: int = Depends(get_page_user_id),
        session: AsyncSession = Depends(get_db)
):
    try:
        await task_service.toggle_status(session, task_id, user_id)
    except TaskError:
        pass
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/tasks/{task_id}/delete")
async def handle_delete_task(
        task_id: int,
        user_id: int = Depends(get_page_user_id),
        session: AsyncSession = Depends(get_db)
):
    try:
        await task_service.delete_task(session, task_id, user_id)
    except TaskError:
        pass
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/api/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def api_create_task(
        task_in: TaskCreate,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
):
    return await task_service.create_task(
        session=session, title=task_in.title, owner_id=current_user.id, description=task_in.description
    )


@router.get("/api/tasks", response_model=List[TaskResponse])
async def api_read_tasks(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
):
    return await task_service.get_tasks_by_owner(session, current_user.id)


@router.patch("/api/tasks/{task_id}", response_model=TaskResponse)
async def api_update_task(
        task_id: int,
        task_in: TaskUpdate,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
):
    try:
        return await task_service.update_task(
            session=session,
            task_id=task_id,
            user_id=current_user.id,
            **task_in.model_dump(exclude_unset=True)
        )
    except TaskNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except TaskAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@router.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def api_delete_task(
        task_id: int,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
):
    try:
        await task_service.delete_task(session, task_id, current_user.id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except TaskAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)