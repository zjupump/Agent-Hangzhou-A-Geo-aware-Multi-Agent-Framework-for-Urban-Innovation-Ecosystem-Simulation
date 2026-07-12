from .base_agent import BaseAgent
from typing import Any, Dict, Optional, Tuple


class EntrepreneurAgent(BaseAgent):
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
        super().__init__(uid, "entrepreneur", position, attributes, config, goals, preferences, seed)
        self.state.setdefault("ideas", [])
        self.state.setdefault("network_strength", self.attributes.get("network_strength", 1.0))
        self.state.setdefault("company_stage", self.attributes.get("company_stage", "idea"))
        self.state.setdefault("funding_need", self.attributes.get("funding_need", 100.0))

    def decide(self, perceptions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        idea_quality = self.state["innovation"] + self.state["network_strength"] * self.rng.uniform(0.1, 0.3)
        target_investor = None
        if perceptions:
            investors = perceptions.get("investors", [])
            if investors:
                investors = sorted(investors, key=lambda inv: inv.state.get("capital", 0.0), reverse=True)
                target_investor = investors[0]
        return {"idea_quality": idea_quality, "preferred_investor": target_investor}

    def act(self, environment: Any, decisions: Optional[Dict[str, Any]] = None) -> None:
        idea_quality = decisions.get("idea_quality", 0.0)
        self.state["ideas"].append({"quality": idea_quality, "step": environment.current_step if hasattr(environment, "current_step") else None})
        investor = decisions.get("preferred_investor")
        if investor and hasattr(environment, "match_investor"):
            environment.match_investor(self, [investor], self.state["funding_need"])