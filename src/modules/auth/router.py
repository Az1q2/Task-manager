from fastapi import APIRouter, Depends, Form, Request, Response, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError
import sys

from src.db.dependencies import get_db
from src.utils.templates import templates
from src.modules.auth import service as auth_service
from src.modules.auth.service import AuthError
from src.modules.auth.schemas import UserRegister, UserLogin, UserInfo, LoginResponse

router = APIRouter(tags=["Auth"])


@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    if request.cookies.get("user_id"):
        return templates.TemplateResponse(
            request=request, name="login.html", context={"request": request, "already_logged_in": True}
        )
    return templates.TemplateResponse(request=request, name="login.html", context={"request": request})


@router.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html", context={"request": request})


@router.post("/login")
async def handle_page_login(
        request: Request,
        login: str = Form(...),
        password: str = Form(...),
        session: AsyncSession = Depends(get_db)
):
    try:
        user_data = UserLogin(login=login, password=password)
        user = await auth_service.authenticate_user(session, user_data)

        redirect = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        redirect.set_cookie(key="user_id", value=str(user.id), httponly=True)
        return redirect

    except ValidationError as e:
        error_msg = e.errors()[0].get("msg")
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"request": request, "error": error_msg, "login_value": login}
        )
    except AuthError as e:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"request": request, "error": e.message, "login_value": login}
        )
    except Exception as e:
        print(f"[LOGIN ERROR DETECTED]: {str(e)}", file=sys.stderr)

        error_text = getattr(e, "message", "Неверный логин или пароль или внутренняя ошибка сервера")
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"request": request, "error": error_text, "login_value": login}
        )


@router.post("/register")
async def handle_page_register(
        request: Request,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        password_confirm: str = Form(...),
        session: AsyncSession = Depends(get_db)
):
    try:
        user_data = UserRegister(
            username=username, email=email, password=password, password_confirm=password_confirm
        )
        await auth_service.register_user(session, user_data)
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        error_msg = e.errors()[0].get("msg")
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"request": request, "error": error_msg, "username_value": username, "email_value": email}
        )
    except AuthError as e:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"request": request, "error": e.message, "username_value": username, "email_value": email}
        )
    except Exception as e:
        # Ловим любые непредвиденные сбои при регистрации
        print(f"[REGISTER ERROR DETECTED]: {str(e)}", file=sys.stderr)
        error_text = getattr(e, "message", "Произошла ошибка при регистрации. Проверьте введенные данные.")
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"request": request, "error": error_text, "username_value": username, "email_value": email}
        )


@router.get("/logout")
async def logout_user():
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="user_id")
    return response


@router.post("/api/auth/login", response_model=LoginResponse)
async def api_login(user_data: UserLogin, response: Response, session: AsyncSession = Depends(get_db)):
    try:
        user = await auth_service.authenticate_user(session, user_data)
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)

    response.set_cookie(key="user_id", value=str(user.id), httponly=True)
    return LoginResponse(user=UserInfo.model_validate(user))