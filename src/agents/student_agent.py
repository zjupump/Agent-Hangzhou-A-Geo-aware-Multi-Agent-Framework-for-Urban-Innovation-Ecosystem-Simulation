from .base_agent import BaseAgent
from typing import Any, Dict, Optional, Tuple


class StudentAgent(BaseAgent):
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
        super().__init__(uid, "student", position, attributes, config, goals, preferences, seed)
        self.state.setdefault("learning", 0.0)
        self.state.setdefault("career_opportunities", [])
        self.state.setdefault("education", self.attributes.get("education", 0.0))
        self.state.setdefault("career_goal", self.preferences.get("career_goal", "innovation"))

    def decide(self, perceptions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        opportunities = perceptions.get("opportunities", []) if perceptions else []
        if opportunities:
            opportunities = sorted(
                opportunities,
                key=lambda opp: opp.get("alignment", 0.0),
                reverse=True,
            )
        target = opportunities[0] if opportunities else None
        learn_rate = 0.1 + self.state["learning"] * 0.05
        return {"target_opportunity": target, "learn_rate": learn_rate}

    def act(self, environment: Any, decisions: Optional[Dict[str, Any]] = None) -> None:
        self.state["learning"] += decisions.get("learn_rate", 0.0)
        target = decisions.get("target_opportunity")
        if target and hasattr(environment, "offer_opportunity"):
            environment.offer_opportunity(self, target)
        if self.state["learning"] > 1.0:
            self.state["education"] += 0.5