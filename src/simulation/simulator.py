from __future__ import annotations
from typing import Any, Dict, Iterable, List, Optional

# ...existing code...
class Simulator:
    def __init__(self, environment: Any, agents: List[Any], config: Optional[Dict[str, Any]] = None):
        self.environment = environment
        self.agents = agents
        self.config = config or {}
        self.current_step = 0
        self.max_steps = self.config.get("max_steps", 100)
        self.log_steps = self.config.get("log_steps", False)

    def step(self) -> None:
        for agent in list(self.agents):
            if agent.active:
                agent.step(self.environment)
        self.current_step += 1
        if self.log_steps:
            self._log_step()

    def run(self, steps: Optional[int] = None) -> Dict[str, Any]:
        max_steps = steps or self.max_steps
        while self.current_step < max_steps:
            self.step()
        return self._collect_results()

    def _collect_results(self) -> Dict[str, Any]:
        return {
            "steps": self.current_step,
            "agent_states": [agent.serialize() for agent in self.agents],
            "environment": getattr(self.environment, "serialize", lambda: {})(),
        }

    def _log_step(self) -> None:
        print(f"Simulator step {self.current_step}")
