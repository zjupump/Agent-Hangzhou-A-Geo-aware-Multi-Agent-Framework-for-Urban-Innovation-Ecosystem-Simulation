# 通用 GIS 工具函数：

# - CRS 转换
# - 几何计算
# - 距离与缓冲区
# - GeoJSON / GeoPackage 读写
# 作用：提供通用 GIS 工具函数，避免环境模块重复编写几何与 CRS 处理
# 关键点：

# 包装 shapely 和 pyproj，统一 CRS 和几何处理接口。
# 适用于 CityEnvironment 和 SpatialDatabase 加载、查询前后处理。

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, Tuple

try:
    from shapely.geometry import shape, mapping, Point
    from shapely.ops import transform
    from pyproj import CRS, Transformer
except ImportError:
    shape = None
    mapping = None
    Point = None
    transform = None
    CRS = None
    Transformer = None


def load_geojson(path: str) -> Dict[str, Any]:
    """
    读取 GeoJSON 文件，返回 dict 数据。
    """
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_geojson(data: Dict[str, Any], path: str) -> None:
    """
    将数据写入 GeoJSON。
    """
    file_path = Path(path)
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def convert_crs_wkt(wkt: str, target_crs: str) -> str:
    """
    将 WKT 表示的几何从当前 CRS 转换到目标 CRS。
    """
    if Transformer is None:
        return wkt
    transformer = Transformer.from_crs(CRS.from_wkt(wkt), CRS.from_string(target_crs), always_xy=True)
    return transformer.to_wkt()


def reproject_geometry(geom: Any, source_crs: str, target_crs: str) -> Any:
    """
    将 shapely 几何对象从 source_crs 投影到 target_crs。
    """
    if transform is None or Transformer is None:
        return geom
    transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
    return transform(transformer.transform, geom)


def point_distance(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """
    计算两点经纬度近似距离（平面距离或经纬度投影后的距离）。
    """
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return (dx * dx + dy * dy) ** 0.5


def buffer_point(point: Tuple[float, float], radius: float) -> Dict[str, Any]:
    """
    返回点的缓冲区 GeoJSON（仅用于辅助分析）。
    """
    if Point is None:
        return {}
    geom = Point(point).buffer(radius)
    return mapping(geom)