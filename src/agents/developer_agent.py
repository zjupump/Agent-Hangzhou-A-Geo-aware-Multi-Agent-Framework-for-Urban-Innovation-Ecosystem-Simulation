from .base_agent import BaseAgent
from typing import Any, Dict, Optional, Tuple


class DeveloperAgent(BaseAgent):
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
        super().__init__(uid, "developer", position, attributes, config, goals, preferences, seed)
        self.state.setdefault("project_pipeline", [])
        self.state.setdefault("build_capacity", self.attributes.get("build_capacity", 1.0))
        self.state.setdefault("desired_salary", self.attributes.get("desired_salary", 0.0))
        self.state.setdefault("employer", self.attributes.get("employer"))

    def decide(self, perceptions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        hotspots = perceptions.get("innovation_hotspots", []) if perceptions else []
        target_location = hotspots[0] if hotspots else self.position
        investment_share = self.rng.uniform(0.05, 0.15)
        investment = min(self.state["wealth"] * investment_share, self.attributes.get("capital", 0.0))
        return {"investment": investment, "target_location": target_location}

    def act(self, environment: Any, decisions: Optional[Dict[str, Any]] = None) -> None:
        if not decisions:
            return
        investment = decisions.get("investment", 0.0)
        if investment <= 0:
            return
        self.state["wealth"] -= investment
        self.state["project_pipeline"].append(
            {"investment": investment, "location": decisions["target_location"], "step": environment.current_step if hasattr(environment, "current_step") else None}
        )
        if hasattr(environment, "allocate_project"):
            environment.allocate_project(self, decisions)