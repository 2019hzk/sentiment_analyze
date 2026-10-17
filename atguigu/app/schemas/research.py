from pydantic import BaseModel, field_validator


class ResearchRequest(BaseModel):
    query: str

    @field_validator("query")
    @staticmethod
    def not_empty(query: str) -> str:
        text = query.strip()

        if not text:
            raise ValueError(f"输入的研究内容不能为空")

        return text


class ResearchResponse(BaseModel):
    task_id: str


class ResearchResultsResponse(BaseModel):
    """各角色研究结果聚合响应体"""
    task_id: str
    results: dict[str, str] = Field(default_factory=dict)
