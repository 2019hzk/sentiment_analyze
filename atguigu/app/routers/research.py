from fastapi import APIRouter

from atguigu.app.dependencies import ResearchServiceDep
from atguigu.app.schemas.research import ResearchRequest, ResearchResponse, ResearchResultsResponse

router = APIRouter(prefix="/api/research", tags=["研究路由"])


@router.post("", response_model=ResearchResponse)
async def start_research_endpoint(payload: ResearchRequest, service: ResearchServiceDep):
    task_id = service.start_research(payload.query)
    return ResearchResponse(task_id=task_id)


@router.get("/results", response_model=ResearchResultsResponse, description="获取研究结果接口")
def get_research_result_endpoint(
        service: ResearchServiceDep,
        task_id: str
):
    """获取指定研究任务的各角色结果"""
    resolved_task_id, research_results = service.get_research_results(task_id)
    return ResearchResultsResponse(task_id=resolved_task_id, results=research_results)
