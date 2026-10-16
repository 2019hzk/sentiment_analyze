from fastapi import FastAPI

from atguigu.app.exceptions.exception_handlers import register_exception_handlers
from atguigu.app.routers.hello import router
from atguigu.app.routers import system
from atguigu.app.services.lifecycle import lifecycle_manager


async def lifespan(app: FastAPI):
    """应用启停时注册与关闭生命周期管理器"""
    try:
        lifecycle_manager.register()
        yield
    finally:
        await lifecycle_manager.shutdown()


app = FastAPI(description="FASTAPI实例", lifespan=lifespan)
app.include_router(router)
app.include_router(system.router)

register_exception_handlers(app)
