from dataclasses import dataclass

from typing import Literal

RoleId = Literal["insight", "media", "host", "report"]


@dataclass(slots=True)
class RoleMetadata:
    """
    定义不同角色Agent的元信息
    """
    llm_config_prefix: str


ROLE_METADATA: dict[RoleId, RoleMetadata] = {
    "insight": RoleMetadata(llm_config_prefix="INSIGHT_AGENT"),
    "media": RoleMetadata(llm_config_prefix="MEDIA_AGENT"),
    "host": RoleMetadata(llm_config_prefix="HOST_AGENT"),
    "report": RoleMetadata(llm_config_prefix="REPORT_ENGINE")
}
