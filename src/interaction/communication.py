from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from ..agents.base_agent import BaseAgent


@dataclass
class Relationship:
    source: str
    target: str
    strength: float = 1.0
    relation_type: str = "professional"
    metadata: Dict[str, Any] = field(default_factory=dict)


class SocialNetwork:
    def __init__(self):
        self.relations: Dict[Tuple[str, str], Relationship] = {}
        self.adjacency: Dict[str, List[str]] = {}

    def add_relation(
        self,
        source: BaseAgent,
        target: BaseAgent,
        strength: float = 1.0,
        relation_type: str = "professional",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        key = (source.uid, target.uid)
        self.relations[key] = Relationship(
            source=source.uid,
            target=target.uid,
            strength=strength,
            relation_type=relation_type,
            metadata=metadata or {},
        )
        self.adjacency.setdefault(source.uid, [])
        if target.uid not in self.adjacency[source.uid]:
            self.adjacency[source.uid].append(target.uid)

    def neighbors(self, agent: BaseAgent) -> List[str]:
        return self.adjacency.get(agent.uid, [])

    def relation_strength(self, source: BaseAgent, target: BaseAgent) -> float:
        return self.relations.get((source.uid, target.uid), Relationship(source.uid, target.uid)).strength

    def broadcast(
        self,
        sender: BaseAgent,
        topic: str,
        message: Dict[str, Any],
        max_hops: int = 1,
    ) -> List[Dict[str, Any]]:
        delivered = []
        for neighbor_uid in self.neighbors(sender):
            delivered.append(
                {"sender": sender.uid, "receiver": neighbor_uid, "topic": topic, "message": message}
            )
        return delivered

    def direct_message(
        self,
        sender: BaseAgent,
        receiver: BaseAgent,
        topic: str,
        message: Dict[str, Any],
    ) -> Dict[str, Any]:
        if receiver.uid in self.neighbors(sender):
            return {"sender": sender.uid, "receiver": receiver.uid, "topic": topic, "message": message}
        return {"sender": sender.uid, "receiver": receiver.uid, "topic": topic, "message": message, "warning": "no direct link"}

    def knowledge_spillover(
        self,
        source: BaseAgent,
        targets: List[BaseAgent],
        intensity: float = 0.1,
    ) -> None:
        for target in targets:
            delta = intensity * source.state.get("innovation", 0.0)
            target.state["innovation"] = target.state.get("innovation", 0.0) + delta

    def form_startup_team(
        self,
        entrepreneur: BaseAgent,
        candidates: List[BaseAgent],
        min_strength: float = 0.3,
        required_size: int = 3,
    ) -> List[BaseAgent]:
        team = [entrepreneur]
        for candidate in candidates:
            if len(team) >= required_size:
                break
            if self.relation_strength(entrepreneur, candidate) >= min_strength:
                team.append(candidate)
        return team

    def developer_job_search(
        self,
        developer: BaseAgent,
        available_positions: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        for position in available_positions:
            if position["role"] == "developer" and position["salary"] >= developer.attributes.get("desired_salary", 0.0):
                return position
        return None

    def graduate_student(
        self,
        student: BaseAgent,
        university: BaseAgent,
        destination: Optional[Tuple[float, float]] = None,
        environment: Optional[Any] = None,
    ) -> None:
        student.state["status"] = "graduated"
        student.state["education"] = student.state.get("education", 0) + 1
        if destination:
            student.position = destination
        if environment and hasattr(environment, "register_alumni"):
            environment.register_alumni(student, university)

    def migrate_student(
        self,
        student: BaseAgent,
        destination: Tuple[float, float],
        environment: Optional[Any] = None,
    ) -> None:
        student.position = destination
        student.state["migration_count"] = student.state.get("migration_count", 0) + 1
        if environment and hasattr(environment, "update_agent_location"):
            environment.update_agent_location(student, destination)

    def developer_jump(
        self,
        developer: BaseAgent,
        new_employer: BaseAgent,
        environment: Optional[Any] = None,
    ) -> None:
        developer.state["employer"] = new_employer.uid
        developer.state["job_changes"] = developer.state.get("job_changes", 0) + 1
        if environment and hasattr(environment, "reassign_employee"):
            environment.reassign_employee(developer, new_employer)

    def connect_institutions(
        self,
        university: BaseAgent,
        company: BaseAgent,
        government: BaseAgent,
        relation_strength: float = 0.8,
    ) -> None:
        self.add_relation(university, company, strength=relation_strength, relation_type="research")
        self.add_relation(company, university, strength=relation_strength, relation_type="innovation")
        self.add_relation(government, university, strength=relation_strength, relation_type="policy")
        self.add_relation(government, company, strength=relation_strength, relation_type="regulation")

    def resolve_conflict(
        self,
        requester: BaseAgent,
        responder: BaseAgent,
        topic: str,
        environment: Optional[Any] = None,
    ) -> Dict[str, Any]:
        resolution = {"requester": requester.uid, "responder": responder.uid, "topic": topic, "status": "negotiation"}
        if environment and hasattr(environment, "log_conflict"):
            environment.log_conflict(requester, responder, topic)
        return resolution
