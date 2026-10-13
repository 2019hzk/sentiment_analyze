"""Insight 与 Media 研究图共享的状态契约"""
from typing import TypedDict, TypeVar, Generic


class SectionState(TypedDict, total=False):
    """完成规划后在研究图中持续传递的章节状态"""
    section_key: str
    title: str
    body: str



SectionStateT = TypeVar("SectionStateT", bound=SectionState)


class ResearchGraphState(TypedDict, Generic[SectionStateT], total=False):
    """
    研究图全流程共享的章节与报告状态
    全程只读的东西走 ResearchRunContext 注入节点，不进 state，所以两个 Agent 都是用空字典 `ainvoke({})` 启动图的。

    Generic[SectionStateT]：泛型类的参数化声明
    ①：用于类定义中
    ②：一个泛型容器，它内部的某些类型是可变的、不固定的
    ③：需要在实例化时使用时传入具体的类型

    伪代码：
    # 定义时使用 Generic[T]
    class Container(Generic[T]):
        item: T

    # 使用时传入具体类型
    user_container: Container[UserSectionState] = Container()

    type[SectionStateT]：
    ①：用于函数参数、返回值或变量的类型注解中（如工厂函数）
    ②：指代“类对象本身”，而不是类的具体实例
    ③：需要传入具体的类（或满足约束的子类），以便在运行时进行实例化

    伪代码：
    def create_state_instance(state_cls: type[SectionStateT]) -> SectionStateT:
    # 接收的是类本身，通过类创建并返回实例
    return state_cls()

    # 调用时传入类，而不是实例
    instance = create_state_instance(SectionState)
    """
    sections: list[SectionStateT]
    cursor: int
    final_report: str
