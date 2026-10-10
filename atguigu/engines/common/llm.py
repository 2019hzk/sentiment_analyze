"""
封装LLM客户端
提供根据角色返回对应角色的客户端、调用LLM的方法（文本内容、结构化对象）

"""
import asyncio
from typing import TypeVar

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from pydantic import BaseModel, Field

from atguigu.engines.common.retryer import with_retry
from atguigu.engines.contract.config import get_config_settings
from atguigu.engines.contract.role import RoleId, ROLE_METADATA

from langchain.chat_models import init_chat_model

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """
    llm客户端
    """

    def __init__(self,
                 model_name: str,
                 model_provider: str,
                 api_key: str,
                 base_url: str
                 ):
        self.model_name = model_name
        self.model_provider = model_provider
        self.api_key = api_key
        self.base_url = base_url

    @classmethod
    def from_role(cls, role: RoleId) -> "LLMClient":
        """
        职责：根据不同的Agent角色 获取对应角色LLM客户端
        :param role:
        :return:
        """

        # 1. 根据角色Id获取到对应的LLM配置信息
        llm_config_prefix = ROLE_METADATA[role].llm_config_prefix

        # 2. 获取settings
        config_settings = get_config_settings()
        return cls(
            model_name=getattr(config_settings, f"{llm_config_prefix}_MODEL_NAME"),
            model_provider=getattr(config_settings, f"{llm_config_prefix}_MODEL_PROVIDER"),
            api_key=getattr(config_settings, f"{llm_config_prefix}_API_KEY"),
            base_url=getattr(config_settings, f"{llm_config_prefix}_BASE_URL")

        )

    @with_retry
    async def generate_text(self,
                            system_prompt: str,
                            user_prompt: str) -> str:
        """
        1. 获取到chat_model实例
        2. 调用LLM
        3. 获取响应的文本内容

        使用流式的方式获取非流式的输出结果。
        优点：针对长文本生成，可以减少服务端网络超时的发生。
        面试：如果调用LLM非常耗时【长文本】，怎么保证能够拿到最终文本的内容。

        :param system_prompt:
        :param user_prompt:
        :return:
        """

        # 1. 将用户以及系统的提示词内容封装到标准的消息对象中
        messages = _build_messages(system_prompt, user_prompt)

        # 2. 创建chat_model的实例对象
        chat_model = self._get_chat_model()

        # 3. 调用
        final_texts: list[str] = []
        try:
            async for chunk in chat_model.astream(messages):
                if text := chunk.text:
                    final_texts.append(text)
        except Exception as exc:
            raise ValueError(f"{self.model_name}返回文本失败:{str(exc)}")

        # 4. 返回
        return "".join(final_texts)

    @with_retry
    async def generate_object(self,
                              system_prompt: str,
                              user_prompt: str,
                              structed_object: type[T]
                              ) -> T:
        """
        json_object：输出的是一个json格式字符串（提示词：返回JSON格式）
        function_calling:API(层面) 现代大语言模型都支持工具调用（广）
        json_schema:最稳的（物理）---->保证一定获取结构化对象【deepseek模型处理】--最准

        :param system_prompt:
        :param user_prompt:
        :param structed_object:
        :return:
        """

        # 1. 将用户以及系统的提示词内容封装到标准的消息对象中
        messages = _build_messages(system_prompt, user_prompt)

        # 2. 创建chat_model的实例对象
        chat_model = self._get_chat_model()

        # 3. 为模型调用时去指定结构化输出
        structed_runnable_object = chat_model.with_structured_output(structed_object, method="json_schema")

        # 4. 调用
        try:
            structed_response = await structed_runnable_object.ainvoke(messages)
        except Exception as exc:
            raise ValueError(f"{self.model_name} 返回结构化对象失败:{str(exc)}")

        if structed_response is None:
            raise ValueError(f"{self.model_name}返回结构化对象为None")

        return structed_response

    def _get_chat_model(self) -> BaseChatModel:
        return init_chat_model(
            model_provider=self.model_provider,
            model=self.model_name,
            api_key=self.api_key,
            base_url=self.base_url
        )


def _build_messages(system_prompt: str,
                    user_prompt: str) -> list[BaseMessage]:
    return [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]


async def generate_text_test():
    llm_client = LLMClient.from_role("host")

    system_prompt = "你是一个讲笑话的专家"
    user_prompt = "请给我讲一个幽默的笑话，一定要让我笑"

    result = await llm_client.generate_text(system_prompt, user_prompt)

    print(result)


class User(BaseModel):
    name: str = Field(description="用户的名字")
    age: int = Field(description="用户的年龄")
    skills: list[str] = Field(description="用户掌握的技能")


async def generate_object_test():
    llm_client = LLMClient.from_role("insight")

    system_prompt = "你是一个数据提取专家，请严格按照要求的格式提取信息。"
    user_prompt = "张三今年 28 岁，精通 Python、LangChain 和 Docker。"
    result = await llm_client.generate_object(system_prompt, user_prompt, User)

    print(f"输出的结构化对象类型{type(result)}")
    print(f"输出的结构化对象{result}")
    print(f"输出的结构化对象名字:{result.name}")
    print(f"输出的结构化对象年龄:{result.age}")
    print(f"输出的结构化对象技能包:{result.skills}")


if __name__ == '__main__':
    # asyncio.run(generate_text_test())
    asyncio.run(generate_object_test())

    # llm_client = LLMClient.from_role("insight")
    # print(llm_client.model_name)
    # print(llm_client.model_provider)
    # print("==============")
    # llm_client1 = LLMClient.from_role("media")
    # print(llm_client1.model_name)
    # print(llm_client1.model_provider)
    # print("==============")
    # llm_client2 = LLMClient.from_role("host")
    # print(llm_client2.model_name)
    # print(llm_client2.model_provider)
    # print("==============")
    # llm_client3 = LLMClient.from_role("report")
    # print(llm_client3.model_name)
    # print(llm_client3.model_provider)
    #
    # prompt_template = ChatPromptTemplate.from_template(template="我的名字是{name}")
