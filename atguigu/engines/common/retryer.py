"""
自定义重试器：控制重试的粒度可控（重试几次、重试间隔）

"""
import asyncio
from dataclasses import dataclass
from functools import wraps
from typing import Callable

from loguru import logger


@dataclass(slots=True)
class RetryConfig:
    init_delay: float = 1.0
    max_delay: float = 60.0  # 控制重试次数
    max_retry: int = 3
    backoff_factor: float = 2.0  # 参与重试间隔的计算

    def get_retry_delay(self, fun_name: str, exc: Exception, attempt: int) -> float | None:
        """
        职责：
        1. 是否能重试，如果能重试，根据重试的次数返回重试的延时
        2. 如果不能重试，直接返回None
        :param attempt:
        :return:
        """

        # 1. 判断是否能够进行重试
        if not self._is_retryable(exc):
            return None

        # 2. 能够进行重试
        delay = self._compute_retry_delay(attempt)

        # 3. 日志输出
        logger.warning(f"函数{fun_name}失败{exc},开始进行{attempt + 1}重试")

        return delay

    def _is_retryable(self, exc: Exception) -> bool:
        """
        职责：返回是否可以重试
        逻辑：从异常对象中获取状态码。
        客户端的4xx状态态码：401、403不能进行重试，429（服务端限流，允许重试）
        服务端的500状态码：500(不是我们自己服务端内部抛出来的状态码，而是第三方服务抛出的500，允许继续重试)
        :return:
        条件： 400<=status_code<500 and status_code!=429---->不能让它重试，否则都可以进行重试
        """

        # 1. 根据异常对象获取服务端的响应状态码
        status_code = self._extract_status_code(exc)

        # 2. 排除客户端的429状态码，不能进行重试
        if isinstance(status_code, int) and 400 <= status_code < 500 and status_code != 429:
            return False
        # 3. 其他的状态码都可以进行重试（None）
        return True

    def _extract_status_code(self, exc: Exception) -> int | None:
        """
        职责：提取异常中的状态码
        :param exc:
        :return:
        """
        # 1. 先从Exception对象中获取status_code属性
        status_code = getattr(exc, 'status_code', None)

        if status_code is not None:
            return status_code

        # 2. 在继续冲Exception对象中获取response属性
        response = getattr(exc, 'response', None)

        # 3. 继续从response对象中获取status_code
        return getattr(response, 'status_code', None)

    def _compute_retry_delay(self, attempt: int) -> float:
        """
        职责：根据重试次数计算延时
        delay=init_delay*(backoff_factor**attempt)
        :param attempt:
        :return:
        """
        return min(self.init_delay * (self.backoff_factor ** attempt), self.max_delay)


retry_config = RetryConfig()


def with_retry(func: Callable):
    """
    装饰器函数【装饰体】
    需要完成重试的逻辑
    装饰逻辑：在执行目标方法期间，如果发现出现了异常，能够继续重试

    :return:
    """
    # 1、判断目标方法是不是携程对象
    if not asyncio.iscoroutinefunction(func):
        raise TypeError("重试器只能装饰异步函数，不能装饰同步函数")

    # 2.定义装饰体函数
    @wraps(func)  # 获取目标函数的元信息
    async def wrapper(*args, **kwargs):
        """
        职责：
        1. 执行目标方法
        2. 判断是否出现异常，如果出现异常，继续执行目标方法
        :return:
        """
        for attempt in range(retry_config.max_retry):
            try:
               return await func(*args, **kwargs)  # 执行目标方法(解包还原)
            except Exception as exc:
                delay = retry_config.get_retry_delay(func.__name__, exc, attempt)
                if delay is None:
                    break
                await asyncio.sleep(delay)

    return wrapper
