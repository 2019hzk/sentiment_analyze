from dataclasses import dataclass

from typing import Literal

RoleId = Literal["insight", "media", "host", "report"]


@dataclass(slots=True)
class RoleMetadata:
    """
    定义不同角色Agent的元信息
    """
    llm_config_prefix: str
    display_name: str


ROLE_METADATA: dict[RoleId, RoleMetadata] = {
    "insight": RoleMetadata(llm_config_prefix="INSIGHT_AGENT", display_name="私域检索专家"),
    "media": RoleMetadata(llm_config_prefix="MEDIA_AGENT", display_name="公域检索专家"),
    "host": RoleMetadata(llm_config_prefix="HOST_AGENT", display_name="研判专家"),
    "report": RoleMetadata(llm_config_prefix="REPORT_ENGINE", display_name="报告引擎")
}


def get_role_display_name(role_id: RoleId) -> str:
    """返回角色的中文展示名"""
    return ROLE_METADATA[role_id].display_name
