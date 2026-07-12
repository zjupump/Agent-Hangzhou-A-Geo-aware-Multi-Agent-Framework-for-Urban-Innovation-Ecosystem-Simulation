````markdown
# Agent-Hangzhou: Geo-aware Multi-Agent Framework for Urban Innovation Ecosystem Simulation

Agent Hangzhou 是一个面向城市创新生态系统的地理感知多智能体仿真框架，结合 GIS 数据与智能体行为，支持环境感知、空间交互与实验管理。

## 核心目标

- 将城市地理环境与智能体决策融合
- 支持杭州城市级别的空间要素：边界、POI、住房、路网、就业、机构
- 提供统一的智能体框架与可扩展环境接口
- 支持可配置场景与参数化实验运行

## 主要特性

- 通用 `BaseAgent` 框架
  - 唯一 ID、角色、位置
  - 状态、目标、偏好、学习与记忆
  - 统一感知、决策、行动、学习循环
  - 可重复性控制（随机种子）

- 四类基础智能体
  - `DeveloperAgent`
  - `EntrepreneurAgent`
  - `InvestorAgent`
  - `StudentAgent`

- GIS 城市环境层
  - `CityEnvironment`
  - `SpatialDatabase`
  - `TransportNetwork`
  - `DynamicEnvironment`
  - 通用 GIS 工具与空间单元定义

- 智能体交互模块
  - `communication.py`
  - `economy.py`

- 实验与仿真管理
  - `Simulator`
  - `ExperimentManager`
  - 配置驱动的场景与参数扫描

## 项目结构

- `src/agents/`
  - `base_agent.py`
  - `developer_agent.py`
  - `entrepreneur_agent.py`
  - `investor_agent.py`
  - `student_agent.py`

- `src/environment/`
  - `base_environment.py`
  - `city_environment.py`
  - `spatial_database.py`
  - `spatial_units.py`
  - `transport_network.py`
  - `dynamic_environment.py`
  - `gis_utils.py`

- `src/interaction/`
  - `communication.py`
  - `economy.py`

- `src/simulation/`
  - `experiment_manager.py`
  - `simulator.py`

- `src/configuration.py`

## 环境模块说明

### CityEnvironment
城市环境管理器，负责：
- 加载空间数据
- 维护 `boundaries`、`poi`、`housing`、`transport`、`employment`、`institutions`
- 为智能体提供 `query_agent_view`、`query_location`、`query_zone`、`query_accessibility`
- 提供业务接口：就业注册、公司注册、毕业生流动、项目分配、融资、职业机会、位置更新、跳槽
- 推进时间步 `step()` 并执行环境动态更新

### SpatialDatabase
空间数据层接口，支持：
- PostGIS 连接与关闭
- 空间表结构创建
- 边界、POI、路网、住房、就业、机构等导入
- `query_point`、`query_nearest`、`query_within_radius`
- `query_zone_by_point`、`query_travel_time`
- CRS 处理与空间投影

### TransportNetwork
路网与可达性模块，负责：
- 路网加载
- 最短路径计算
- 出行时间估计
- 不同交通模式支持

### DynamicEnvironment
动态演化模块，负责：
- 租金与房价变化
- 就业机会变化
- 企业生命周期演进
- 交通供给变化
- 政策干预与补贴事件

### GIS 工具
`gis_utils.py` 提供：
- GeoJSON 读写
- CRS 与投影转换
- 几何计算、距离与缓冲区生成

## 智能体模块说明

### BaseAgent
统一智能体基类，提供：
- `perceive()`
- `decide()`
- `act()`
- `learn()`
- `step()`
- `serialize()`
- `snapshot()` / `restore()`
- 随机性与可重复性控制

### 四类 Agent
- `DeveloperAgent`：项目投资、建筑开发、跳槽决策
- `EntrepreneurAgent`：创业构团队、融资配对、公司成长
- `InvestorAgent`：投资决策、风险分配、组合管理
- `StudentAgent`：学习与就业选择、毕业迁移、职业机会评估

## 开发与运行

1. 安装依赖
2. 配置 `config.yaml`、PostGIS 数据库连接与空间数据路径
3. 使用 `ExperimentManager` 加载场景并运行仿真

## 未来扩展

- 完善 PostGIS + OSM 数据导入流程
- 补全路网可达性与公共交通分析
- 加强智能体互动与经济机制
- 增加多尺度空间单元与城市网格支持
- 扩展实验管理与参数扫描能力
````