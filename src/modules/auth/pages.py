from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from src.db.dependencies import get_db
from src.modules.auth import service as auth_service
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.templates import templates
from src.modules.auth.schemas import UserLogin, UserRegister
from pydantic import ValidationError
router = APIRouter(tags=["Auth Pages"])


@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    auth_cookie = request.cookies.get("user_id")

    if auth_cookie:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"already_logged_in": True}
        )

    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )

@router.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


@router.post("/login")
async def handle_page_login(
        request: Request,
        login: str = Form(...),
        password: str = Form(...),
        session: AsyncSession = Depends(get_db)
):
    user_data = UserLogin(login=login, password=password)
    user = await auth_service.authenticate_user(session, user_data)

    if not user:
        return templates.TemplateResponse(
            context={"request": request, "error": "Неверный логин или пароль"},
            name="login.html"
        )

    redirect = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    redirect.set_cookie(key="user_id", value=str(user.id), httponly=True)
    return redirect


@router.post("/register")
async def handle_page_register(
        request: Request,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        password_confirm: str = Form(...),
        session: AsyncSession = Depends(get_db)
):
    if password != password_confirm:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "Пароли не совпадают"}
        )

    try:
        user_data = UserRegister(
            username=username,
            email=email,
            password=password,
            password_confirm=password_confirm
        )
    except ValidationError as e:
        error_msg = e.errors()[0].get("msg")
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": error_msg}
        )

    result = await auth_service.register_user(session, user_data)

    if isinstance(result, str) or not result:
        error_msg = result if isinstance(result, str) else "Не удалось создать пользователя"
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": error_msg}
        )

    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/logout")
async def logout_user():
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="user_id")
    return response

