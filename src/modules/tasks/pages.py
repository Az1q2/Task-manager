from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.dependencies import get_db
from src.modules.tasks import service as task_service
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Task Pages"])
templates = Jinja2Templates(directory="src/templates")


@router.get("/", response_class=HTMLResponse)
async def get_home_page(
        request: Request,
        search: str = None,
        session: AsyncSession = Depends(get_db)
):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    tasks = await task_service.get_tasks_by_owner(session, owner_id=int(user_id))

    if tasks is None:
        tasks = []

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


from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession


@router.post("/register")
async def handle_page_register(
        request: Request,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        password_confirm: str = Form(...),
):
    error_message = None

    if len(username) < 3:
        error_message = "Имя пользователя должно содержать минимум 3 символа."
    elif len(password) < 6:
        error_message = "Пароль должен содержать минимум 6 символов."

    elif password != password_confirm:
        error_message = "Пароли не совпадают."
    if error_message:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error": error_message,
                "username_value": username,
                "email_value": email
            }
        )
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/tasks/create", response_class=HTMLResponse)
async def create_task_page(request: Request):
    if not request.cookies.get("user_id"):
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(request=request, name="task_form.html")

@router.post("/tasks/create")
async def create_task(
        request: Request,
        title: str = Form(...),
        description: str = Form(None),
        session: AsyncSession = Depends(get_db)
):
    user_id = request.cookies.get("user_id")
    await task_service.create_task(session, title=title, description=description, owner_id=int(user_id))
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/tasks/{task_id}/edit", response_class=HTMLResponse)
async def edit_task_page(task_id: int, request: Request, session: AsyncSession = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    task = await task_service.get_task_by_id(session, task_id)


    if not task or task.owner_id != int(user_id):
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name="task_edit.html",
        context={"task": task}
    )

@router.post("/tasks/{task_id}/edit")
async def edit_task(
        task_id: int,
        request: Request,
        title: str = Form(...),
        description: str = Form(None),
        session: AsyncSession = Depends(get_db)
):
    user_id = request.cookies.get("user_id")
    await task_service.update_task(
        session=session,
        task_id=task_id,
        user_id=int(user_id),
        title=title,
        description=description
    )
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/tasks/{task_id}/toggle")
async def toggle_task_status(
        task_id: int,
        request: Request,
        session: AsyncSession = Depends(get_db)
):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    await task_service.toggle_status(session, task_id, int(user_id))

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/tasks/{task_id}/delete")
async def delete_task(
        task_id: int,
        request: Request,
        session: AsyncSession = Depends(get_db)
):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    await task_service.delete_task(session, task_id, int(user_id))
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)