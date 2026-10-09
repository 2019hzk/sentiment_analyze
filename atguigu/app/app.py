from fastapi import FastAPI

from atguigu.app.exceptions.exception_handlers import register_exception_handlers
from atguigu.app.routers.hello import router
from atguigu.app.routers import system

app = FastAPI(description="FASTAPI实例")
app.include_router(router)
app.include_router(system.router)

register_exception_handlers(app)
