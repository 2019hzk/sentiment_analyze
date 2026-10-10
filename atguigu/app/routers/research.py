from fastapi import APIRouter

from atguigu.app.dependencies import ResearchServiceDep
from atguigu.app.schemas.research import ResearchRequest, ResearchResponse

router = APIRouter(prefix="/api/research", tags=["研究路由"])


@router.post("", response_model=ResearchResponse)
async def start_research_endpoint(payload: ResearchRequest, service: ResearchServiceDep):
    task_id = service.start_research(payload.query)
    return ResearchResponse(task_id=task_id)
