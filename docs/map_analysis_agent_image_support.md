# 地图分析智能体图片分析功能

## 概述

地图分析智能体 (`MapAnalysisAgent`) 现在支持使用军事地形图图片分析工具 (`MilitaryImageMapAnalyzer`) 来分析地形图图片，提供专业的军事地形分析服务。

## 功能特性

### 核心能力
- **图片地形图分析**: 分析地形图图片，识别地形特征和军事价值
- **地形分类识别**: 自动识别山地、平原、丘陵等地形类型
- **关键地标提取**: 识别重要的地形标志和参考点
- **军事价值评估**: 评估地形的战术价值和军事意义
- **战术建议生成**: 基于地形特点提供具体的战术建议

### 分析要素
1. **地形特征**: 山地、平原、河流、森林等地形类型
2. **高程分析**: 海拔高度、坡度、地势起伏
3. **水文条件**: 河流、湖泊、沼泽等水体分布
4. **植被覆盖**: 森林、草地、农田等植被类型
5. **人工设施**: 道路、桥梁、建筑物等基础设施
6. **军事要素**: 观察条件、掩护条件、机动路线等

## 配置说明

### 工具配置
在 `configs/military_config.toml` 中，地图分析智能体已配置了以下工具：

```toml
[agent.map_analysis_agent_config]
model_id = "claude37-sonnet-thinking"
name = "map_analysis_agent"
description = "地图分析专家，负责分析作战地区地形地貌，提供地形利用建议"
max_steps = 8
template_path = "src/agent/map_analysis_agent/prompts/map_analysis_agent.yaml"
tools = ["military_map_analyzer", "military_image_map_analyzer"]
```

### 工具参数
`military_image_map_analyzer` 工具支持以下参数：

- `image_path` (必需): 地形图图片文件路径
- `analysis_focus` (可选): 分析重点
  - `terrain`: 地形分析
  - `tactical`: 战术分析  
  - `infrastructure`: 基础设施
  - `comprehensive`: 综合分析 (默认)
- `mission_context` (可选): 任务背景
  - `offensive`: 攻击任务 (默认)
  - `defensive`: 防御任务
  - `reconnaissance`: 侦察任务
  - `logistics`: 后勤任务
- `scale_reference` (可选): 地图比例尺参考信息

## 使用示例

### 基本使用
```python
# 创建地图分析智能体
from src.agent.map_analysis_agent import MapAnalysisAgent

# 分析任务
task = """
请分析地形图图片 'path/to/terrain_map.jpg'，
分析重点为综合分析，任务背景为攻击作战，
提供详细的地形分析报告。
"""

result = await map_agent.run(task)
```

### 详细任务示例
```python
task = """
请使用 military_image_map_analyzer 工具分析以下地形图：

1. 图片路径: 'examples/sample_terrain_map.jpg'
2. 分析重点: 'comprehensive' (综合分析)
3. 任务背景: 'offensive' (攻击任务)

请提供包含以下内容的详细分析报告：
- 地形分类和特征描述
- 关键地标和参考点
- 高程特征和坡度分析
- 植被覆盖和水系分布
- 基础设施识别
- 军事价值评估
- 战术建议和机动路线
- 可见性和隐蔽条件分析
"""
```

## 输出结果

分析工具将返回结构化的分析结果，包括：

```python
{
    "terrain_classification": "地形分类",
    "elevation_features": {"高程特征": "详细信息"},
    "key_landmarks": ["关键地标列表"],
    "vegetation_analysis": {"植被类型": "覆盖情况"},
    "water_features": ["水系特征列表"],
    "infrastructure": ["基础设施列表"],
    "military_assessment": {"军事评估": "战术价值"},
    "tactical_recommendations": ["战术建议列表"],
    "visibility_analysis": {"可见性": "分析结果"},
    "movement_corridors": ["机动走廊列表"]
}
```

## 测试示例

运行测试示例：
```bash
python examples/test_map_analysis_with_image.py
```

## 注意事项

1. **图片格式**: 支持常见的图片格式 (JPG, PNG, BMP等)
2. **图片质量**: 建议使用高清晰度的地形图图片以获得更好的分析效果
3. **比例尺**: 如果知道地图比例尺，建议在分析时提供以提高分析精度
4. **任务背景**: 根据实际军事任务选择合适的任务背景以获得针对性的分析建议

## 相关文件

- 智能体实现: `src/agent/map_analysis_agent/map_analysis_agent.py`
- 工具实现: `src/tools/military_image_map_analyzer.py`
- 提示词模板: `src/agent/map_analysis_agent/prompts/map_analysis_agent.yaml`
- 配置文件: `configs/military_config.toml`
- 测试示例: `examples/test_map_analysis_with_image.py` 