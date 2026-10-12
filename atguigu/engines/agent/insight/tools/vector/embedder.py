"""BGE-M3 稠密向量编码器。"""

from functools import cache
from typing import Iterable

from FlagEmbedding import BGEM3FlagModel

from atguigu.engines.contract.config import get_config_settings


@cache
def _load_model() -> BGEM3FlagModel:
    """按配置创建 BGE-M3 向量模型"""
    settings = get_config_settings()
    device = settings.INSIGHT_EMBEDDING_DEVICE

    return BGEM3FlagModel(
        settings.INSIGHT_EMBEDDING_MODEL,
        use_fp16=bool(device and "cpu" not in device.lower()),
        devices=device
    )


def encode_dense(texts: Iterable[str]) -> list[list[float]]:
    """生成稠密向量"""
    text_items = list(texts)
    model_output = _load_model().encode(
        text_items,
        return_dense=True,
        return_sparse=False
    )

    return [dense.tolist() for dense in model_output["dense_vecs"]]


if __name__ == '__main__':
    print(encode_dense(["我喜欢你"]))
