# 使用 ABC 提供抽象方法。
# load_data、query_agent_view、step、serialize 是必须实现接口。
# src/environment/base_environment.py
# 统一环境基类，定义所有环境子类应实现的接口：

# load_data()
# query_agent_view(agent)
# step()
# serialize() / snapshot()
# 这样可以让 CityEnvironment 继承并保持可扩展。




from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseEnvironment(ABC):
    """
    统一环境基类，定义城市环境必须提供的通用接口。
    这样可以让不同环境实现共享结构和流程。
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config or {}
        self.current_step = 0

    @abstractmethod
    def load_data(self) -> None:
        """
        加载环境所需的空间和属性数据。
        子类应实现数据初始化逻辑。
        """
        raise NotImplementedError

    @abstractmethod
    def query_agent_view(self, agent: Any) -> Dict[str, Any]:
        """
        为智能体提供基于其位置和角色的环境感知信息。
        """
        raise NotImplementedError

    @abstractmethod
    def step(self) -> None:
        """
        推进环境时间步，执行动态变化逻辑。
        """
        raise NotImplementedError

    @abstractmethod
    def serialize(self) -> Dict[str, Any]:
        """
        将环境状态序列化为可保存/分析的字典结构。
        """
        raise NotImplementedError

    def snapshot(self) -> Dict[str, Any]:
        """
        默认快照方法，可用于恢复或日志记录。
        """
        return {"step": self.current_step, "config": self.config}