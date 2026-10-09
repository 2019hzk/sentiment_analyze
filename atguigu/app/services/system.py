import os
from typing import Any

from dotenv import set_key

from atguigu.engines.contract.config import get_config_settings, ENV_FILE, reload_config_settings

ALLOWED_CONFIG_KEYS = [
    "DB_HOST", "DB_PORT", "DB_USER", "DB_NAME",
    "INSIGHT_AGENT_API_KEY", "INSIGHT_AGENT_BASE_URL", "INSIGHT_AGENT_MODEL_NAME", "INSIGHT_AGENT_MODEL_PROVIDER",
    "MEDIA_AGENT_API_KEY", "MEDIA_AGENT_BASE_URL", "MEDIA_AGENT_MODEL_NAME", "MEDIA_AGENT_MODEL_PROVIDER",
    "REPORT_ENGINE_API_KEY", "REPORT_ENGINE_BASE_URL", "REPORT_ENGINE_MODEL_NAME", "REPORT_ENGINE_MODEL_PROVIDER",
    "HOST_AGENT_API_KEY", "HOST_AGENT_BASE_URL", "HOST_AGENT_MODEL_NAME", "HOST_AGENT_MODEL_PROVIDER",
    "ANSPIRE_API_KEY", "ANSPIRE_BASE_URL"
]


def mark_secret(value: str) -> str:
    if not value:
        return value

    return f"****{value[-4:]}"


class SystemConfigService:
    def get_system_config(self) -> dict[str, Any]:
        config_info: dict[str, Any] = {}
        config_settings = get_config_settings()
        for key in ALLOWED_CONFIG_KEYS:
            value = getattr(config_settings, key, None)
            value_text = value if value is not None else ""

            if key.endswith("_API_KEY"):
                value_text = mark_secret(value_text)

            config_info[key] = value_text

        return config_info

    def update_system_config(self, update_config_info: dict[str, Any]):
        """
        将字典中最新的key对应的value值写入到【ConfigSettings or .env文件中 接着reload_config_settings】
        :param update_config_info:
        :return:
        """
        unknown_keys = [key for key in update_config_info if key not in ALLOWED_CONFIG_KEYS]

        if unknown_keys:
            raise ValueError(f"unknown key:{f'、'.join(unknown_keys)}")

        for key, value in update_config_info.items():
            set_key(ENV_FILE, key, value,quote_mode="never")  # 更新.env
            os.environ[key] = value  # 更新环境变量

        reload_config_settings()
