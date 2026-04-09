import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
# from src.modules.router import router as auth_router
# from src.modules.router import router as user_router
# from src.modules.router import router as task_router
from src.utils.templates import templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/static"), name="static")
@app.get("/")
def index_page(
    request: Request
):
    return templates.TemplateResponse(
        request=request,
        name="base.html")

@app.get('/login')
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )

if __name__ == "__main__":
    uvicorn.run('main:app', reload=True)

# app.include_router(auth_router, prefix="/auth", tags=["auth"])
# app.include_router(user_router, prefix="/users", tags=["users"])
# app.include_router(task_router, prefix="/task", tags=["task"])