import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.modules.auth.router import router as auth_router
from src.modules.users.router import router as users_router
from src.modules.tasks.router import router as tasks_router
from src.modules.auth.pages import router as pages_router
from src.modules.tasks.pages import router as tasks_pages_router
app = FastAPI(title="Task Manager API")

app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(pages_router)
app.include_router(tasks_pages_router)

if __name__ == "__main__":
    uvicorn.run('main:app', reload=True)