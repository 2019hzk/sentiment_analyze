from fastapi import APIRouter

from atguigu.app.dependencies import SystemConfigServiceDep
from atguigu.app.schemas.system import SystemConfigResponse, SystemConfigRequest

router = APIRouter(prefix="/api/config", tags=["系统配置路由"])


@router.get("", response_model=SystemConfigResponse)
async def get_system_config_endpoint(service: SystemConfigServiceDep):
    config_info = service.get_system_config()
    return SystemConfigResponse(config=config_info)


@router.post("")
async def update_system_config_endpoint(request: SystemConfigRequest, service: SystemConfigServiceDep):
    service.update_system_config(request.root)
