from .base_agent import BaseAgent
from typing import Any, Dict, Optional, Tuple


class InvestorAgent(BaseAgent):
    def __init__(
        self,
        uid: str,
        position: Optional[Tuple[float, float]] = None,
        attributes: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        goals: Optional[list[str]] = None,
        preferences: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = None,
    ):
        super().__init__(uid, "investor", position, attributes, config, goals, preferences, seed)
        self.state.setdefault("capital", self.attributes.get("capital", 100.0))
        self.state.setdefault("portfolio", [])
        self.state.setdefault("risk_tolerance", self.attributes.get("risk_tolerance", 0.5))

    def decide(self, perceptions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        candidates = perceptions.get("entrepreneurs", []) if perceptions else []
        if candidates:
            candidates = sorted(candidates, key=lambda e: e.state.get("innovation", 0.0), reverse=True)
        target = candidates[0] if candidates else None
        allocation = 0.0
        if target:
            share = self.rng.uniform(0.1, self.state["risk_tolerance"])
            allocation = min(self.state["capital"] * share, self.state["capital"])
        return {"allocation": allocation, "target": target}

    def act(self, environment: Any, decisions: Optional[Dict[str, Any]] = None) -> None:
        amount = decisions.get("allocation", 0.0)
        target = decisions.get("target")
        if amount <= 0 or not target:
            return
        self.state["capital"] -= amount
        self.state["portfolio"].append({"entrepreneur": target.uid, "amount": amount, "step": environment.current_step if hasattr(environment, "current_step") else None})
        if hasattr(environment, "invest_in"):
            environment.invest_in(self, target, amount)