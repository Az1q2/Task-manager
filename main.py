import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from src.modules.auth.router import router as auth_router
from src.modules.users.router import router as users_router
from src.modules.tasks.router import router as tasks_router
from src.utils.templates import templates

app = FastAPI(title="Task Manager API")

app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tasks_router)
@app.get("/")
def index_page(request: Request):
    return templates.TemplateResponse(request, 'base.html')

if __name__ == "__main__":
    uvicorn.run('main:app', reload=True)