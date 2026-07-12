# 处理环境随时间变化的机制：

# - 租金变化、房价变化
# - 就业岗位动态增减
# - 企业生命周期
# - 交通供给变化
# - 政策干预、补贴、基础设施建设

# 作用：处理时间推进下环境动态变化，支持租金、就业、企业、交通、政策等演化。
# 让环境动态逻辑集中在一个模块，便于后续扩展。
# 接口与 CityEnvironment.step() 对接。

from __future__ import annotations
from typing import Any, Dict, List, Optional


class DynamicEnvironment:
    """
    环境动态演化模块。
    负责模型运行过程中环境状态的时变更新。
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config or {}
        self.policy_events: List[Dict[str, Any]] = []

    def update_rent(self, housing: Dict[str, Any], step: int) -> None:
        """
        根据时间步和城市态势更新租金水平。
        """
        growth = self.config.get("rent_growth_rate", 0.01)
        housing["default_rent"] = housing.get("default_rent", 3000) * (1 + growth)

    def update_employment(self, employment: Dict[str, Any], step: int) -> None:
        """
        更新就业机会和岗位数。
        """
        delta = self.config.get("job_growth", 0)
        employment["available_jobs"] = max(0, employment.get("available_jobs", 0) + delta)

    def update_transport(self, transport: Dict[str, Any], step: int) -> None:
        """
        更新路网供给、公共交通服务或拥堵情况。
        """
        transport["service_level"] = transport.get("service_level", 1.0)

    def update_companies(self, companies: Dict[str, Any], step: int) -> None:
        """
        更新企业生命周期、融资、失败概率等。
        """
        for company in companies.values():
            if company.get("capital", 0) < 0:
                company["status"] = "failed"

    def apply_policy(self, policy: Dict[str, Any]) -> None:
        """
        执行政策干预，如补贴、税收、研发投入。
        """
        self.policy_events.append(policy)

    def step(self, environment: Any) -> None:
        """
        环境时间推进入口，调用各子模块更新函数。
        """
        self.update_rent(environment.housing, environment.current_step)
        self.update_employment(environment.employment, environment.current_step)
        self.update_transport(environment.transport, environment.current_step)
        self.update_companies(environment.companies, environment.current_step)