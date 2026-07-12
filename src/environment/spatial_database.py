
# 实现 SpatialDatabase 类
# 支持 PostGIS 连接、建表、关闭
# 定义数据加载接口和空间查询接口
# 统一 CRS 参数
# 提供 query_point、query_nearest、query_within_radius、query_zone_by_point、query_travel_time
# SpatialDatabase 提供 PostGIS 连接和常见空间查询接口
from __future__ import annotations
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:  # pragma: no cover
    psycopg2 = None
    RealDictCursor = None


class SpatialDatabase:
    def __init__(self, db_config: Optional[Dict[str, Any]] = None):
        self.db_config = db_config or {}
        self.default_crs = self.db_config.get("crs", "EPSG:4326")
        self.connection = None
        self.cursor = None
        self.metadata: Dict[str, Any] = {
            "source": self.db_config.get("source", {}),
            "version": self.db_config.get("version", "unknown"),
            "loaded_at": None,
        }

    def connect(self) -> None:
        if self.connection:
            return
        if psycopg2 is None:
            raise ImportError("psycopg2 is required for PostGIS connection")
        self.connection = psycopg2.connect(
            host=self.db_config.get("host", "localhost"),
            port=self.db_config.get("port", 5432),
            dbname=self.db_config.get("dbname", "agent_hangzhou"),
            user=self.db_config.get("user", "postgres"),
            password=self.db_config.get("password", "postgres"),
        )
        self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)

    def close(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        self.connection = None
        self.cursor = None

    def create_schema(self) -> None:
        self._ensure_connected()
        sql = """
        CREATE EXTENSION IF NOT EXISTS postgis;
        CREATE TABLE IF NOT EXISTS boundaries (
            gid SERIAL PRIMARY KEY,
            name TEXT,
            properties JSONB,
            geom geometry(MultiPolygon, {srid})
        );
        CREATE TABLE IF NOT EXISTS poi (
            gid SERIAL PRIMARY KEY,
            name TEXT,
            category TEXT,
            properties JSONB,
            geom geometry(Point, {srid})
        );
        CREATE TABLE IF NOT EXISTS housing (
            gid SERIAL PRIMARY KEY,
            type TEXT,
            price NUMERIC,
            capacity INTEGER,
            geom geometry(Polygon, {srid})
        );
        CREATE TABLE IF NOT EXISTS employment (
            gid SERIAL PRIMARY KEY,
            employer_uid TEXT,
            role TEXT,
            salary NUMERIC,
            requirements JSONB,
            geom geometry(Point, {srid})
        );
        CREATE TABLE IF NOT EXISTS institutions (
            gid SERIAL PRIMARY KEY,
            name TEXT,
            institution_type TEXT,
            properties JSONB,
            geom geometry(Point, {srid})
        );
        CREATE TABLE IF NOT EXISTS transport_network (
            gid SERIAL PRIMARY KEY,
            edge_id TEXT,
            mode TEXT,
            travel_time NUMERIC,
            geom geometry(LineString, {srid})
        );
        """.format(srid=self._srid())
        self._execute(sql)

    def load_boundary(self, path: str, table_name: str = "boundaries") -> Dict[str, Any]:
        return self._load_geojson(path, table_name)

    def load_poi(self, path: str, table_name: str = "poi") -> Dict[str, Any]:
        return self._load_geojson(path, table_name)

    def load_osm_network(self, path: str, table_name: str = "transport_network") -> Dict[str, Any]:
        return self._load_geojson(path, table_name)

    def load_housing(self, path: str, table_name: str = "housing") -> Dict[str, Any]:
        return self._load_geojson(path, table_name)

    def load_employment(self, path: str, table_name: str = "employment") -> Dict[str, Any]:
        return self._load_geojson(path, table_name)

    def load_institutions(self, path: str, table_name: str = "institutions") -> Dict[str, Any]:
        return self._load_geojson(path, table_name)

    def query_point(self, point: Tuple[float, float], layer: str) -> Dict[str, Any]:
        self._ensure_connected()
        sql = f"""
        SELECT * FROM {layer}
        WHERE ST_Contains(
            geom,
            ST_SetSRID(ST_Point(%s, %s), {self._srid()})
        )
        LIMIT 1;
        """
        self.cursor.execute(sql, (point[0], point[1]))
        return self.cursor.fetchone() or {}

    def query_nearest(self, point: Tuple[float, float], layer: str, k: int = 5) -> List[Dict[str, Any]]:
        self._ensure_connected()
        sql = f"""
        SELECT *, ST_Distance(geom, ST_SetSRID(ST_Point(%s, %s), {self._srid()})) AS distance
        FROM {layer}
        ORDER BY geom <-> ST_SetSRID(ST_Point(%s, %s), {self._srid()})
        LIMIT %s;
        """
        self.cursor.execute(sql, (point[0], point[1], point[0], point[1], k))
        return self.cursor.fetchall() or []

    def query_within_radius(
        self,
        point: Tuple[float, float],
        radius: float,
        layer: str,
    ) -> List[Dict[str, Any]]:
        self._ensure_connected()
        sql = f"""
        SELECT *
        FROM {layer}
        WHERE ST_DWithin(
            geom,
            ST_SetSRID(ST_Point(%s, %s), {self._srid()}),
            %s
        );
        """
        self.cursor.execute(sql, (point[0], point[1], radius))
        return self.cursor.fetchall() or []

    def query_zone_by_point(
        self,
        point: Tuple[float, float],
        zone_layer: str = "taz",
    ) -> Dict[str, Any]:
        self._ensure_connected()
        sql = f"""
        SELECT *
        FROM {zone_layer}
        WHERE ST_Contains(
            geom,
            ST_SetSRID(ST_Point(%s, %s), {self._srid()})
        )
        LIMIT 1;
        """
        self.cursor.execute(sql, (point[0], point[1]))
        return self.cursor.fetchone() or {}

    def query_travel_time(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        mode: str = "drive",
    ) -> Dict[str, Any]:
        if self.connection is None or self.cursor is None:
            distance = math.hypot(destination[0] - origin[0], destination[1] - origin[1])
            speed = {"walk": 5.0, "bike": 15.0, "drive": 40.0, "transit": 25.0}.get(mode, 5.0)
            return {"mode": mode, "distance": distance, "travel_time": distance / speed if speed else None}
        sql = f"""
        SELECT travel_time
        FROM transport_network
        WHERE mode = %s
        ORDER BY geom <-> ST_SetSRID(ST_Point(%s, %s), {self._srid()})
        LIMIT 1;
        """
        self.cursor.execute(sql, (mode, origin[0], origin[1]))
        record = self.cursor.fetchone()
        return {"mode": mode, "travel_time": record["travel_time"] if record else None}

    def reproject(self, geom_wkt: str, target_crs: str) -> str:
        self._ensure_connected()
        target_srid = self._crs_to_srid(target_crs)
        sql = "SELECT ST_AsText(ST_Transform(ST_GeomFromText(%s, %s), %s)) AS geom;"
        self.cursor.execute(sql, (geom_wkt, self._srid(), target_srid))
        record = self.cursor.fetchone()
        return record["geom"] if record else geom_wkt

    def _load_geojson(self, path: str, table_name: str) -> Dict[str, Any]:
        self._ensure_connected()
        file_path = Path(path)
        if not file_path.exists():
            return {}
        with file_path.open("r", encoding="utf-8") as f:
            content = json.load(f)
        for feature in content.get("features", []):
            geom = json.dumps(feature["geometry"])
            properties = json.dumps(feature.get("properties", {}))
            sql = f"""
            INSERT INTO {table_name} (properties, geom)
            VALUES (%s, ST_SetSRID(ST_GeomFromGeoJSON(%s), {self._srid()}));
            """
            self.cursor.execute(sql, (properties, geom))
        self.connection.commit()
        return {"table": table_name, "features": len(content.get("features", []))}

    def _ensure_connected(self) -> None:
        if self.connection is None or self.cursor is None:
            self.connect()

    def _srid(self) -> int:
        return self._crs_to_srid(self.default_crs)

    @staticmethod
    def _crs_to_srid(crs: str) -> int:
        if isinstance(crs, int):
            return crs
        if crs.upper().startswith("EPSG:"):
            return int(crs.split(":")[1])
        return 4326
    




# SpatialDatabase 类
# 支持 PostGIS 连接
# 支持 connect(), close()
# 支持 create_schema()，建立空间表结构
# 支持数据导入方法：
# load_boundary(...)
# load_poi(...)
# load_osm_network(...)
# load_housing(...)
# load_employment(...)
# load_institutions(...)
# 支持查询方法：
# query_point(point)
# query_nearest(point, layer, k)
# query_within_radius(point, radius, layer)
# query_zone_by_point(point)
# query_travel_time(origin, destination, mode)
# 处理 CRS：
# 从 config 读取默认 CRS
# 提供 reproject(geom, target_crs)
# 记录数据来源、版本、时间戳
# 如果需要，后面可以把 PostGIS 连接改成 SQLAlchemy/GeoAlchemy2。