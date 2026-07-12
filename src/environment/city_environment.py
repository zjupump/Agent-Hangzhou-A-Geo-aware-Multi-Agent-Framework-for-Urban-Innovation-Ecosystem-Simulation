# 构造时接收 config 和可选的 spatial_db
# 维护边界、poi、housing、transport、employment、institutions
# 提供统一的 Agent 接口：query_agent_view、query_location、query_zone、query_accessibility
# 提供业务接口：register_employment、register_company、register_alumni、allocate_project、invest_in、offer_opportunity、update_agent_location、reassign_employee
# 提供时间推进 step() 和动态更新 _update_dynamics()
#CityEnvironment 改成了真正的环境管理器，换成配置驱动、空间数据库驱动。


from __future__ import annotations
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .spatial_database import SpatialDatabase


class CityEnvironment:
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        spatial_db: Optional[SpatialDatabase] = None,
    ):
        self.config = config or {}
        self.spatial_db = spatial_db or SpatialDatabase(self.config.get("database", {}))
        self.crs = self.config.get("crs", self.spatial_db.default_crs)
        self.current_step = 0
        self.time = self.config.get("start_time", 0)
        self.boundaries: Dict[str, Any] = {}
        self.poi: Dict[str, Any] = {}
        self.housing: Dict[str, Any] = {}
        self.transport: Dict[str, Any] = {}
        self.employment: Dict[str, Any] = {}
        self.institutions: Dict[str, Any] = {}
        self.agents: List[Any] = []
        self.projects: List[Dict[str, Any]] = []
        self.companies: Dict[str, Any] = {}
        self.alumni: List[Dict[str, Any]] = []

        self._load_environment()

    def _load_environment(self) -> None:
        self.spatial_db.connect()
        data_paths = self.config.get("data_paths", {})

        if data_paths.get("boundary"):
            self.boundaries = self.spatial_db.load_boundary(data_paths["boundary"])
        if data_paths.get("poi"):
            self.poi = self.spatial_db.load_poi(data_paths["poi"])
        if data_paths.get("housing"):
            self.housing = self.spatial_db.load_housing(data_paths["housing"])
        if data_paths.get("transport"):
            self.transport = self.spatial_db.load_osm_network(data_paths["transport"])
        if data_paths.get("employment"):
            self.employment = self.spatial_db.load_employment(data_paths["employment"])
        if data_paths.get("institutions"):
            self.institutions = self.spatial_db.load_institutions(data_paths["institutions"])

    def query_agent_view(self, agent: Any) -> Dict[str, Any]:
        return {
            "position": agent.position,
            "zone": self.query_zone(agent.position),
            "nearby_poi": self.spatial_db.query_nearest(agent.position, layer="poi", k=5),
            "accessibility": self.query_accessibility(
                agent.position,
                self.config.get("default_mode", "walk"),
            ),
            "local_economy": self.query_location(agent.position),
        }

    def query_location(self, point: Tuple[float, float]) -> Dict[str, Any]:
        if self.spatial_db:
            location_data = self.spatial_db.query_point(point, layer="housing")
        else:
            location_data = {}
        if not location_data:
            location_data = {
                "jobs": self.config.get("default_jobs", 10),
                "rent": self.config.get("default_rent", 3000),
                "metro": self.config.get("default_metro_distance", 1.0),
            }
        return location_data

    def query_zone(self, position: Tuple[float, float]) -> Dict[str, Any]:
        return self.spatial_db.query_zone_by_point(position, zone_layer=self.config.get("zone_layer", "taz"))

    def query_accessibility(self, position: Tuple[float, float], mode: str = "walk") -> Dict[str, Any]:
        if self.spatial_db:
            return self.spatial_db.query_travel_time(position, position, mode=mode)
        speed_map = {"walk": 5.0, "bike": 15.0, "drive": 40.0, "transit": 25.0}
        return {"mode": mode, "estimated_speed": speed_map.get(mode, 5.0)}

    def register_employment(self, candidate: Any, posting: Dict[str, Any]) -> None:
        self.employment.setdefault("filled_positions", []).append(
            {"candidate": candidate.uid, "posting": posting}
        )

    def register_company(self, company: Any) -> None:
        self.companies[company.uid] = company

    def register_alumni(self, student: Any, university: Any) -> None:
        self.alumni.append({"student": student.uid, "university": university.uid})

    def allocate_project(self, developer: Any, decisions: Dict[str, Any]) -> None:
        self.projects.append(
            {
                "developer": developer.uid,
                "investment": decisions.get("investment", 0.0),
                "location": decisions.get("target_location"),
                "step": self.current_step,
            }
        )

    def invest_in(self, investor: Any, entrepreneur: Any, amount: float) -> None:
        self.register_company({"uid": f"company_{entrepreneur.uid}"})
        self.companies.setdefault(f"company_{entrepreneur.uid}", {})["investment"] = amount

    def offer_opportunity(self, student: Any, opportunity: Dict[str, Any]) -> None:
        student.state.setdefault("career_opportunities", []).append(opportunity)

    def update_agent_location(self, agent: Any, destination: Tuple[float, float]) -> None:
        agent.position = destination

    def reassign_employee(self, developer: Any, new_employer: Any) -> None:
        developer.state["employer"] = new_employer.uid

    def step(self) -> None:
        self.current_step += 1
        self.time += 1
        self._update_dynamics()

    def _update_dynamics(self) -> None:
        rent_change = self.config.get("rent_growth_rate", 0.01)
        if isinstance(self.housing, dict):
            self.housing["default_rent"] = self.housing.get("default_rent", 3000) * (1 + rent_change)
        self.employment["available_jobs"] = max(
            0,
            self.employment.get("available_jobs", 100) + self.config.get("job_growth", 0),
        )

    def serialize(self) -> Dict[str, Any]:
        return {
            "current_step": self.current_step,
            "time": self.time,
            "boundaries": self.boundaries,
            "poi": self.poi,
            "housing": self.housing,
            "transport": self.transport,
            "employment": self.employment,
            "institutions": self.institutions,
            "companies": list(self.companies.keys()),
            "projects": self.projects,
            "alumni": self.alumni,
        }
    

# src/environment/city_environment.py
# 需要改成真正的环境管理器，而不是只有 query_location 的占位函数。建议修改点：

# 增加构造参数 config 和 spatial_db
# 加载空间数据库连接、CRS、基础数据路径
# 维护：
# boundaries
# poi
# housing
# transport
# employment
# institutions
# 提供域内通用接口：
# query_agent_view(agent)
# query_location(point)
# query_zone(position)
# query_accessibility(position, mode)
# register_employment(candidate, posting)
# register_company(company)
# register_alumni(student, university)
# allocate_project(developer, decisions)
# invest_in(investor, entrepreneur, amount)
# offer_opportunity(student, opportunity)
# update_agent_location(agent, destination)
# reassign_employee(developer, new_employer)
# 时间推进方法 step() / advance_time()
# 让 CityEnvironment 负责“环境随时间变化”的机制，例如租金、岗位、公共交通供给变化。
# 这样 Simulator 与 Agent 就可以通过统一接口访问环境。