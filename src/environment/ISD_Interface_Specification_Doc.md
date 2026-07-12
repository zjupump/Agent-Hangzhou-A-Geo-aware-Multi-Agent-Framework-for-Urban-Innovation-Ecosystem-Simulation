````markdown
# Agent Hangzhou 环境模块接口说明

本说明文档面向 `src/environment/` 模块，描述当前建议的环境子系统接口与模块协作关系。目标是构建一个可扩展的 GIS 城市环境层，支持智能体感知、空间查询、路网可达性、动态演化和实验复现。

---

## 1. 模块总览

建议环境模块包含以下文件：

- `base_environment.py`
- `city_environment.py`
- `spatial_database.py`
- `spatial_units.py`
- `transport_network.py`
- `dynamic_environment.py`
- `gis_utils.py`

这些模块协同构成：
- 空间数据层（`SpatialDatabase`）
- 城市环境业务层（`CityEnvironment`）
- 路网可达性层（`TransportNetwork`）
- 动态演化层（`DynamicEnvironment`）
- 基础接口与工具层（`BaseEnvironment`、`gis_utils`、`spatial_units`）

---

## 2. `BaseEnvironment` 接口

文件：`src/environment/base_environment.py`

### 目的
定义所有环境类必须实现的统一接口，保证环境系统可扩展和可替换。

### 关键方法
- `__init__(config)`
- `load_data()`
- `query_agent_view(agent)`
- `step()`
- `serialize()`
- `snapshot()`

### 说明
- `load_data()` 用于加载空间数据和初始环境状态。
- `query_agent_view(agent)` 为智能体提供位置与角色相关的环境感知。
- `step()` 执行环境时间推进逻辑。
- `serialize()` 输出可保存和分析的状态。
- `snapshot()` 提供默认状态快照。

---

## 3. `CityEnvironment` 接口

文件：`src/environment/city_environment.py`

### 目的
城市环境管理器，负责环境加载、智能体视图、业务事件和时间推进。

### 关键字段
- `config`
- `spatial_db`
- `crs`
- `current_step`
- `time`
- `boundaries`
- `poi`
- `housing`
- `transport`
- `employment`
- `institutions`
- `agents`
- `projects`
- `companies`
- `alumni`

### 关键方法
- `__init__(config, spatial_db)`
- `_load_environment()`
- `query_agent_view(agent)`
- `query_location(point)`
- `query_zone(position)`
- `query_accessibility(position, mode)`
- `register_employment(candidate, posting)`
- `register_company(company)`
- `register_alumni(student, university)`
- `allocate_project(developer, decisions)`
- `invest_in(investor, entrepreneur, amount)`
- `offer_opportunity(student, opportunity)`
- `update_agent_location(agent, destination)`
- `reassign_employee(developer, new_employer)`
- `step()`
- `_update_dynamics()`
- `serialize()`

### 说明
- `CityEnvironment` 通过 `SpatialDatabase` 提供空间查询，并封装业务语义。
- 负责将智能体行为映射为环境事件，例如岗位注册、公司落地、毕业生流动。
- 支持环境随时间变化的机制，例如租金、就业和交通动态。

---

## 4. `SpatialDatabase` 接口

文件：`src/environment/spatial_database.py`

### 目的
空间数据层接口，管理 PostGIS 连接、数据加载、CRS 和常见空间查询。

### 关键字段
- `db_config`
- `default_crs`
- `connection`
- `cursor`
- `metadata`

### 关键方法
- `__init__(db_config)`
- `connect()`
- `close()`
- `create_schema()`
- `load_boundary(path, table_name)`
- `load_poi(path, table_name)`
- `load_osm_network(path, table_name)`
- `load_housing(path, table_name)`
- `load_employment(path, table_name)`
- `load_institutions(path, table_name)`
- `query_point(point, layer)`
- `query_nearest(point, layer, k)`
- `query_within_radius(point, radius, layer)`
- `query_zone_by_point(point, zone_layer)`
- `query_travel_time(origin, destination, mode)`
- `reproject(geom_wkt, target_crs)`

### 说明
- `SpatialDatabase` 是环境的底层存储与查询接口。
- 支持 PostGIS 连接和 GeoJSON 数据导入。
- 处理 CRS，提供空间要素检索、邻近查询、范围查询和出行时间估计。

---

## 5. `TransportNetwork` 接口

文件：`src/environment/transport_network.py`

### 目的
路网管理与可达性计算，支持多模式交通。

### 关键字段
- `config`
- `graph`
- `node_index`
- `edge_data`

### 关键方法
- `__init__(config)`
- `load_network(source, layer)`
- `add_edge(u, v, travel_time, mode, attributes)`
- `shortest_path(origin_node, destination_node, mode)`
- `travel_time(origin, destination, mode)`
- `accessibility(position, mode, cutoff)`

### 说明
- `TransportNetwork` 负责路网构建、最短路径和服务可达性计算。
- 可与 `SpatialDatabase` 对接读取 OSM / 路网数据。
- 支持驾车、步行、公共交通、自行车等模式。

---

## 6. `DynamicEnvironment` 接口

文件：`src/environment/dynamic_environment.py`

### 目的
环境时变逻辑模块，处理租金、就业、企业、交通和政策演化。

### 关键字段
- `config`
- `policy_events`

### 关键方法
- `__init__(config)`
- `update_rent(housing, step)`
- `update_employment(employment, step)`
- `update_transport(transport, step)`
- `update_companies(companies, step)`
- `apply_policy(policy)`
- `step(environment)`

### 说明
- `DynamicEnvironment` 的 `step()` 与 `CityEnvironment.step()` 对接。
- 使环境动态演化逻辑集中、可扩展。

---

## 7. `gis_utils` 接口

文件：`src/environment/gis_utils.py`

### 目的
通用 GIS 工具函数，避免几何和 CRS 处理重复实现。

### 关键函数
- `load_geojson(path)`
- `write_geojson(data, path)`
- `convert_crs_wkt(wkt, target_crs)`
- `reproject_geometry(geom, source_crs, target_crs)`
- `point_distance(a, b)`
- `buffer_point(point, radius)`

### 说明
- 包装 `shapely` 与 `pyproj`，提供 CRS 转换和几何计算工具。
- 适用于数据加载、空间查询前后处理。

---

## 8. 模块协同关系

- `Simulator` 调用 `CityEnvironment.step()` 推进环境，并依次运行每个智能体。
- 智能体 `perceive()` 调用 `CityEnvironment.query_agent_view(agent)` 获取空间感知。
- 智能体 `act()` 调用 `CityEnvironment` 业务接口触发事件，例如就业、投资、项目落位、迁移。
- `CityEnvironment` 通过 `SpatialDatabase` 执行空间查询与数据加载。
- `CityEnvironment` 可调用 `TransportNetwork` 计算可达性与旅行时间。
- `DynamicEnvironment` 管理环境随时间推进的演化逻辑，供 `CityEnvironment.step()` 使用。
- `gis_utils` 提供几何和 CRS 转换支持。

---

## 9. 设计原则

- 接口统一：所有环境类遵循 `BaseEnvironment` 生命周期。
- 数据分层：空间存储与查询由 `SpatialDatabase` 负责，业务语义由 `CityEnvironment` 负责。
- 可扩展性：路网、动态演化、空间单元为可插拔模块。
- 地理感知：智能体感知接口包含位置、邻域、可达性和本地资源信息。
- 时间演化：环境必须支持 `step()` / `advance_time()`，不能仅停留在静态查询层。

````

1. src/environment/base_environment.py
类：BaseEnvironment
统一环境抽象基类，定义所有环境类型必须实现的接口。

方法
__init__(self, config: Dict[str, Any])

参数：config — 环境配置字典
作用：初始化环境基础配置、时间步变量等。
load_data(self) -> None

作用：加载空间数据和环境初始状态。
子类必须实现。
query_agent_view(self, agent: Any) -> Dict[str, Any]

参数：agent — 当前智能体
返回：智能体感知信息字典
作用：为智能体提供基于位置、类型的环境视图。
step(self) -> None

作用：推进环境时间步，执行动态更新逻辑。
子类必须实现。
serialize(self) -> Dict[str, Any]

返回：环境状态序列化结果
作用：输出环境当前状态，用于保存、日志、分析。
snapshot(self) -> Dict[str, Any]

返回：环境快照
作用：默认提供环境状态备份接口，可用于恢复。
2. src/environment/spatial_database.py
类：SpatialDatabase
空间数据层接口，负责 PostGIS 连接、数据加载、坐标系统和空间查询。

属性
db_config
default_crs
connection
cursor
metadata
方法
__init__(self, db_config: Optional[Dict[str, Any]] = None)

初始化数据库配置与 CRS。
connect(self) -> None

作用：建立 PostGIS 连接。
要求：psycopg2 可用。
close(self) -> None

作用：关闭数据库连接。
create_schema(self) -> None

作用：创建标准空间表结构，包括：
boundaries
poi
housing
employment
institutions
transport_network
load_boundary(self, path: str, table_name: str = "boundaries") -> Dict[str, Any]

load_poi(self, path: str, table_name: str = "poi") -> Dict[str, Any]

load_osm_network(self, path: str, table_name: str = "transport_network") -> Dict[str, Any]

load_housing(self, path: str, table_name: str = "housing") -> Dict[str, Any]

load_employment(self, path: str, table_name: str = "employment") -> Dict[str, Any]

load_institutions(self, path: str, table_name: str = "institutions") -> Dict[str, Any]

作用：导入 GeoJSON / 空间数据到对应表。
query_point(self, point: Tuple[float, float], layer: str) -> Dict[str, Any]

作用：返回某点所在要素属性。
query_nearest(self, point: Tuple[float, float], layer: str, k: int = 5) -> List[Dict[str, Any]]

作用：返回最近 k 个要素。
query_within_radius(self, point: Tuple[float, float], radius: float, layer: str) -> List[Dict[str, Any]]

作用：返回某半径内要素列表。
query_zone_by_point(self, point: Tuple[float, float], zone_layer: str = "taz") -> Dict[str, Any]

作用：返回点所属交通分析区/分区。
query_travel_time(self, origin: Tuple[float, float], destination: Tuple[float, float], mode: str = "drive") -> Dict[str, Any]

作用：估计出行时间，优先使用路网数据。
reproject(self, geom_wkt: str, target_crs: str) -> str

作用：几何投影转换。
_load_geojson(self, path: str, table_name: str) -> Dict[str, Any]

作用：内部 GeoJSON 导入实现。
_ensure_connected(self) -> None

作用：保证数据库已连接。
_srid(self) -> int

作用：返回默认 CRS 的 SRID。
_crs_to_srid(crs: str) -> int

作用：CRS 字符串转换为 SRID。
3. src/environment/city_environment.py
类：CityEnvironment
城市环境管理器，负责环境加载、智能体视图、业务接口和时间推进。

属性
config
spatial_db
crs
current_step
time
boundaries
poi
housing
transport
employment
institutions
agents
projects
companies
alumni
方法
__init__(self, config: Optional[Dict[str, Any]] = None, spatial_db: Optional[SpatialDatabase] = None)

作用：初始化环境，加载空间数据库与环境数据。
_load_environment(self) -> None

作用：调用 SpatialDatabase 加载各种图层数据。
query_agent_view(self, agent: Any) -> Dict[str, Any]

返回：智能体感知信息，如周边 POI、可达性、区域属性、局部就业/租金状况。
query_location(self, point: Tuple[float, float]) -> Dict[str, Any]

作用：查询点位位置属性，至少包含本地就业、租金、便利设施等。
query_zone(self, position: Tuple[float, float]) -> Dict[str, Any]

作用：返回点所属分区/交通分析区信息。
query_accessibility(self, position: Tuple[float, float], mode: str = "walk") -> Dict[str, Any]

作用：返回位置可达性指标，支持多种出行模式。
register_employment(self, candidate: Any, posting: Dict[str, Any]) -> None

作用：记录岗位录用，维护就业库存。
register_company(self, company: Any) -> None

作用：注册新公司实体。
register_alumni(self, student: Any, university: Any) -> None

作用：记录高校毕业生校友关系。
allocate_project(self, developer: Any, decisions: Dict[str, Any]) -> None

作用：记录开发者项目落位与投资。
invest_in(self, investor: Any, entrepreneur: Any, amount: float) -> None

作用：处理投资事件、注册融资。
offer_opportunity(self, student: Any, opportunity: Dict[str, Any]) -> None

作用：向学生提供职业/学习机会。
update_agent_location(self, agent: Any, destination: Tuple[float, float]) -> None

作用：更新智能体地理位置。
reassign_employee(self, developer: Any, new_employer: Any) -> None

作用：处理开发者跳槽。
step(self) -> None

作用：推进环境时间步。
_update_dynamics(self) -> None

作用：执行租金、就业、交通等环境动态更新逻辑。
serialize(self) -> Dict[str, Any]

作用：输出环境当前状态。
4. src/environment/transport_network.py
类：TransportNetwork
路网与可达性计算组件。

属性
config
graph
node_index
edge_data
方法
__init__(self, config: Dict[str, Any]) -> None

初始化路网组件与配置。
load_network(self, source: Any, layer: str = "transport_network") -> None

作用：从 PostGIS、GeoJSON 或其他源加载路网数据，构建图结构。
add_edge(self, u: str, v: str, travel_time: float, mode: str = "drive", attributes: Optional[Dict[str, Any]] = None) -> None

作用：添加路段边。
shortest_path(self, origin_node: str, destination_node: str, mode: str = "drive") -> List[str]

返回：最短路径节点序列。
作用：基于 travel_time 或成本权重计算路径。
travel_time(self, origin: Tuple[float, float], destination: Tuple[float, float], mode: str = "drive") -> Dict[str, Any]

返回：出行时间估计。
作用：支持最近节点匹配与路径分析。
accessibility(self, position: Tuple[float, float], mode: str = "walk", cutoff: float = 30.0) -> Dict[str, Any]

返回：可达性指标，如可达要素数量、平均时间、服务级别。
作用：支持多模式可达性计算。
5. src/environment/dynamic_environment.py
类：DynamicEnvironment
环境动态演化模块，负责随时间更新环境状态。

属性
config
policy_events
方法
__init__(self, config: Dict[str, Any]) -> None

作用：初始化动态演化配置。
update_rent(self, housing: Dict[str, Any], step: int) -> None

作用：根据时间和增长率更新租金水平。
update_employment(self, employment: Dict[str, Any], step: int) -> None

作用：更新就业机会与岗位数。
update_transport(self, transport: Dict[str, Any], step: int) -> None

作用：更新交通供给与服务水平。
update_companies(self, companies: Dict[str, Any], step: int) -> None

作用：更新企业生命周期、资本、失败状态。
apply_policy(self, policy: Dict[str, Any]) -> None

作用：执行政策事件、补贴、法规调控。
step(self, environment: Any) -> None

作用：环境时间步入口，逐项调用更新方法。
6. src/environment/gis_utils.py
工具函数接口
函数
load_geojson(path: str) -> Dict[str, Any]

作用：读取 GeoJSON 文件并返回字典。
write_geojson(data: Dict[str, Any], path: str) -> None

作用：写 GeoJSON 文件。
convert_crs_wkt(wkt: str, target_crs: str) -> str

作用：将 WKT 几何从当前 CRS 转换为目标 CRS。
reproject_geometry(geom: Any, source_crs: str, target_crs: str) -> Any

作用：将 Shapely 几何对象重新投影。
point_distance(a: Tuple[float, float], b: Tuple[float, float]) -> float

作用：计算两点平面距离。
buffer_point(point: Tuple[float, float], radius: float) -> Dict[str, Any]

作用：生成点缓冲区 GeoJSON。
7. 模块间协作关系
Simulator 调用 CityEnvironment.step() 推进环境，调用 agent.step(environment) 推进智能体；
Agent.perceive() 调用 CityEnvironment.query_agent_view(agent)；
Agent.act() 通过 CityEnvironment 提供的业务接口触发事件，如 register_employment、invest_in、allocate_project；
CityEnvironment 内部使用 SpatialDatabase 执行空间查询与数据加载；
CityEnvironment 可调用 TransportNetwork 计算可达性和路网旅行时间；
DynamicEnvironment 负责环境随时间变化的演化逻辑，供 CityEnvironment.step() 使用；
gis_utils 提供几何和 CRS 转换支持，避免重复实现。
8. 关键设计原则
接口统一：所有环境类应遵循 BaseEnvironment 定义的生命周期；
数据分层：SpatialDatabase 负责空间存储与查询，CityEnvironment 负责业务语义；
可扩展性：路网、动态演化、空间单元均作为可插拔模块；
地理感知：智能体感知接口必须包含位置、邻域、可达性和本地资源；
时间演化：环境必须支持 step() / advance_time()，而不是静态查询。