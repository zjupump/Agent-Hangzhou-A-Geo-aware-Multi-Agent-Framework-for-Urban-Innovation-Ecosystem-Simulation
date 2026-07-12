from __future__ import annotations
import random
from typing import Any, Dict, List, Optional, Tuple


class BaseAgent:
    def __init__(
        self,
        uid: str,
        role: str,
        position: Optional[Tuple[float, float]] = None,
        attributes: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        goals: Optional[List[str]] = None,
        preferences: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = None,
    ):
        self.uid = uid
        self.role = role
        self.position = position or (0.0, 0.0)
        self.attributes = attributes or {}
        self.config = config or {}
        self.goals = goals or self.attributes.get("goals", [])
        self.preferences = preferences or self.attributes.get("preferences", {})
        self.seed = seed if seed is not None else self.attributes.get("seed")
        self.rng = random.Random(self.seed)

        self.state: Dict[str, Any] = {
            "wealth": self.attributes.get("wealth", 0.0),
            "innovation": self.attributes.get("innovation", 0.0),
            "trust": self.attributes.get("trust", 0.0),
            "activity": self.attributes.get("activity", 0.0),
            "education": self.attributes.get("education", 0.0),
            "employment_status": self.attributes.get("employment_status", "unemployed"),
            "stress": self.attributes.get("stress", 0.0),
            "population": self.attributes.get("population", 1),
            "goals": self.goals,
            "preferences": self.preferences,
        }

        self.neighbors: List[BaseAgent] = []
        self.history: List[Dict[str, Any]] = []
        self.memory: List[Dict[str, Any]] = []
        self.inbox: List[Dict[str, Any]] = []
        self.active = True

    def perceive(self, environment: Any) -> Dict[str, Any]:
        if hasattr(environment, "query_agent_view"):
            return environment.query_agent_view(self)
        return {}

    def decide(self, perceptions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        raise NotImplementedError("Agent must implement decide()")

    def act(self, environment: Any, decisions: Optional[Dict[str, Any]] = None) -> None:
        raise NotImplementedError("Agent must implement act()")

    def learn(self, feedback: Optional[Dict[str, Any]] = None) -> None:
        if feedback:
            self.memory.append(feedback)
            self.state["innovation"] += feedback.get("innovation_gain", 0.0)

    def update_state(self) -> None:
        self.history.append(self.state.copy())

    def step(self, environment: Any) -> None:
        perceptions = self.perceive(environment)
        decisions = self.decide(perceptions)
        self.act(environment, decisions)
        self.learn({"decisions": decisions})
        self.update_state()

    def add_neighbor(self, agent: BaseAgent) -> None:
        if agent not in self.neighbors:
            self.neighbors.append(agent)

    def receive_message(self, message: Dict[str, Any]) -> None:
        self.inbox.append(message)

    def send_message(
        self,
        receiver: BaseAgent,
        topic: str,
        content: Dict[str, Any],
        network: Optional[Any] = None,
    ) -> None:
        message = {"sender": self.uid, "receiver": receiver.uid, "topic": topic, "content": content}
        receiver.receive_message(message)
        if network and hasattr(network, "add_relation"):
            pass

    def clear_inbox(self) -> None:
        self.inbox.clear()

    def snapshot(self) -> Dict[str, Any]:
        return {
            "uid": self.uid,
            "role": self.role,
            "position": self.position,
            "attributes": self.attributes,
            "config": self.config,
            "state": self.state.copy(),
            "goals": list(self.goals),
            "preferences": dict(self.preferences),
            "history": list(self.history),
            "inbox": list(self.inbox),
        }

    def restore(self, snapshot: Dict[str, Any]) -> None:
        self.position = tuple(snapshot.get("position", self.position))
        self.attributes = snapshot.get("attributes", self.attributes)
        self.config = snapshot.get("config", self.config)
        self.state = snapshot.get("state", self.state)
        self.goals = snapshot.get("goals", self.goals)
        self.preferences = snapshot.get("preferences", self.preferences)
        self.history = snapshot.get("history", self.history)
        self.inbox = snapshot.get("inbox", self.inbox)

    def serialize(self) -> Dict[str, Any]:
        return {
            "uid": self.uid,
            "role": self.role,
            "position": self.position,
            "attributes": self.attributes,
            "config": self.config,
            "state": self.state,
            "goals": self.goals,
            "preferences": self.preferences,
            "history": self.history,
            "inbox": self.inbox,
            "seed": self.seed,
        }