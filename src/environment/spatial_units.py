# src/environment/spatial_units.py
# 定义空间单元系统。建议至少包括：
# 作用：定义多尺度空间单元模型，为城市模拟提供基础空间结构。
# SpatialUnit
# GridCell
# TrafficAnalysisZone
# BuildingBlock
# PointOfInterest
# 用于：
# 网格级别的城市模拟
# 交通分析区层次
# 建筑/街区层次

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class SpatialUnit:
    """
    通用空间单元基类，可扩展为格网、分区、建筑块等。
    """
    uid: str
    centroid: Tuple[float, float]
    area: float
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GridCell(SpatialUnit):
    """
    网格单元，用于网格级别模拟。
    """
    row: int = 0
    col: int = 0
    neighbors: List[str] = field(default_factory=list)


@dataclass
class TrafficAnalysisZone(SpatialUnit):
    """
    交通分析区，适用于 TAZ 层级建模。
    """
    zone_id: str = ""
    population: int = 0
    employment: int = 0
    land_use: Dict[str, float] = field(default_factory=dict)


@dataclass
class BuildingBlock(SpatialUnit):
    """
    建筑街区或楼宇块。
    """
    block_type: str = "mixed"
    capacity: int = 0
    usage: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PointOfInterest(SpatialUnit):
    """
    点位对象，如高校、公司、交通站点、公共设施。
    """
    name: str = ""
    poi_type: str = ""
    category: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

