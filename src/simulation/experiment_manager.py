from pathlib import Path
from typing import Any, Dict, List, Optional

from ..configuration import load_config, merge_config
from ..agents import DeveloperAgent, EntrepreneurAgent, InvestorAgent, StudentAgent
from .simulator import Simulator
from ..environment.city_environment import CityEnvironment


class ExperimentManager:
    def __init__(self, config_path: Optional[str] = None, overrides: Optional[Dict[str, Any]] = None):
        self.global_config = load_config(config_path) if config_path else {}
        self.config = merge_config(self.global_config, overrides or {})

    def build_environment(self, env_config: Dict[str, Any]) -> CityEnvironment:
        return CityEnvironment(env_config)

    def build_agents(self, agents_config: List[Dict[str, Any]]) -> list:
        mapping = {
            "developer": DeveloperAgent,
            "entrepreneur": EntrepreneurAgent,
            "investor": InvestorAgent,
            "student": StudentAgent,
        }
        agents = []
        for agent_spec in agents_config:
            cls = mapping.get(agent_spec.get("role"))
            if not cls:
                continue
            agents.append(
                cls(
                    uid=agent_spec["uid"],
                    position=tuple(agent_spec.get("position", (0.0, 0.0))),
                    attributes=agent_spec.get("attributes", {}),
                    config=agent_spec.get("config", {}),
                )
            )
        return agents

    def run(self, scenario_name: Optional[str] = None) -> Dict[str, Any]:
        scenario = self.config.get("scenarios", {}).get(scenario_name, self.config)
        env = self.build_environment(scenario.get("environment", {}))
        agents = self.build_agents(scenario.get("agents", []))
        simulator = Simulator(env, agents, config=scenario.get("simulation", {}))
        return simulator.run(steps=scenario.get("simulation", {}).get("max_steps", None))

    def parameter_scan(self, experiments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for exp in experiments:
            manager = ExperimentManager(overrides=merge_config(self.global_config, exp))
            results.append(manager.run(exp.get("name")))
        return results