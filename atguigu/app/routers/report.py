from fastapi import APIRouter
from fastapi.responses import Response

from atguigu.app.dependencies import ReportServiceDep

router = APIRouter(prefix="/api/report", tags=["报告路由"])


@router.get("/status", description="获取报告状态")
def get_report_status_endpoint(
        service: ReportServiceDep,
        task_id: str
):
    """查询报告生成状态"""
    return service.get_report_status(task_id)


@router.post("/generate", description="开始生成报告")
async def generate_report_endpoint(task_id: str, service: ReportServiceDep):
    """异步触发生成报告任务"""
    return {"generation_id": service.generate_report(task_id)}


@router.get("/result/{generation_id}", description="获取报告生成结果")
def get_generate_result_endpoint(generation_id: str, service: ReportServiceDep):
    """获取已完成报告 Markdown"""
    markdown_content = service.get_report_result(generation_id)
    return Response(content=markdown_content, media_type="text/markdown")
