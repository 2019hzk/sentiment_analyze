"""全局异常处理器:将领域异常统一映射为 HTTP 响应,路由层不再逐端点 try/except"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger


def register_exception_handlers(app: FastAPI):
    """注册领域异常到 HTTP 状态码的映射,响应体与 HTTPException 同为 {"detail": ...}。"""

    @app.exception_handler(LookupError)
    async def handle_missing_resource(_request: Request, exc: LookupError) -> JSONResponse:
        """将资源不存在异常转换为 404 响应"""
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ValueError)
    async def handle_invalid_input(_request: Request, exc: ValueError) -> JSONResponse:
        """将输入值异常转换为 400 响应"""
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(RuntimeError)
    async def handle_state_conflict(_request: Request, exc: RuntimeError) -> JSONResponse:
        """将运行状态冲突转换为 409 响应"""
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_request: Request, exc: Exception) -> JSONResponse:
        """记录未预期异常并转换为 500 响应"""
        logger.exception(f"未处理的服务端异常: {exc}")
        return JSONResponse(status_code=500, content={"detail": str(exc)})
