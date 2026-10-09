from typing import Any

from pydantic import BaseModel, Field, RootModel, field_validator


class SystemConfigRequest(RootModel):

    @field_validator("root")
    @staticmethod
    def not_empty(value: dict[str, Any]):
        if not value:
            raise ValueError("请求体不能为空")
        return value


class SystemConfigResponse(BaseModel):
    config: dict[str, Any] = Field(default_factory=dict)
