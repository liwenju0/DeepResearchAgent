# 军事地形图图片分析工具

## 概述

`MilitaryImageMapAnalyzer` 是一个专门用于分析军事地形图图片的AI工具。该工具能够识别地形特征、评估军事价值并提供战术建议。

## 功能特性

### 核心功能
1. **地形分析** - 识别地形类型、高程特征和地貌特点
2. **地标识别** - 识别关键地形标志和参考点
3. **植被分析** - 分析植被覆盖类型和密度
4. **水系识别** - 识别河流、湖泊、水渠等水体
5. **基础设施识别** - 识别道路、桥梁、建筑物等人工设施
6. **军事评估** - 评估地形的军事价值和战术意义
7. **战术建议** - 基于地形特点提供战术建议
8. **可见性分析** - 分析观察条件和隐蔽性
9. **机动路线规划** - 识别适合部队机动的路线

### 分析重点选项
- `terrain` - 地形分析：重点关注地形地貌特征和自然环境要素
- `tactical` - 战术分析：重点关注军事战术价值和作战运用建议
- `infrastructure` - 基础设施分析：重点关注基础设施和人工建筑的识别与评估
- `comprehensive` - 综合分析：全面分析所有方面（默认）

### 任务背景选项
- `offensive` - 攻击任务：从攻击作战角度分析，重点关注突击路线和火力支援阵地
- `defensive` - 防御任务：从防御作战角度分析，重点关注防御阵地和阻击要点
- `reconnaissance` - 侦察任务：从侦察任务角度分析，重点关注观察哨位和隐蔽接敌路线
- `logistics` - 后勤任务：从后勤保障角度分析，重点关注补给路线和集结地域

## 使用方法

### 基本用法

```python
from src.tools.military_image_map_analyzer import MilitaryImageMapAnalyzer

# 创建工具实例
analyzer = MilitaryImageMapAnalyzer()

# 执行分析
result = await analyzer.forward(
    image_path="path/to/terrain_map.png",
    analysis_focus="comprehensive",
    mission_context="offensive",
    scale_reference="1:50000"
)

# 查看结果
print(f"地形分类: {result.terrain_classification}")
print(f"军事评估: {result.military_assessment}")
print(f"战术建议: {result.tactical_recommendations}")
```

### 参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `image_path` | str | 是 | 地形图图片文件路径 |
| `analysis_focus` | str | 否 | 分析重点（默认：comprehensive） |
| `mission_context` | str | 否 | 任务背景（默认：offensive） |
| `scale_reference` | str | 否 | 地图比例尺参考信息 |

### 返回结果

工具返回 `ImageMapAnalysisResult` 对象，包含以下字段：

```python
class ImageMapAnalysisResult:
    terrain_classification: str      # 地形分类
    elevation_features: Dict         # 高程特征
    key_landmarks: List[str]         # 关键地标
    vegetation_analysis: Dict        # 植被分析
    water_features: List[str]        # 水系特征
    infrastructure: List[str]        # 基础设施
    military_assessment: Dict        # 军事评估
    tactical_recommendations: List[str]  # 战术建议
    visibility_analysis: Dict        # 可见性分析
    movement_corridors: List[str]    # 机动走廊
```

## 使用示例

### 示例1：综合地形分析

```python
result = await analyzer.forward(
    image_path="terrain_map.png",
    analysis_focus="comprehensive",
    mission_context="offensive",
    scale_reference="1:50000"
)

print(f"地形分类: {result.terrain_classification}")
print(f"关键地标: {result.key_landmarks}")
print(f"军事评估: {result.military_assessment}")
```

### 示例2：防御任务分析

```python
result = await analyzer.forward(
    image_path="terrain_map.png",
    analysis_focus="tactical",
    mission_context="defensive"
)

print(f"防御价值: {result.military_assessment}")
print(f"战术建议: {result.tactical_recommendations}")
```

### 示例3：基础设施分析

```python
result = await analyzer.forward(
    image_path="terrain_map.png",
    analysis_focus="infrastructure",
    mission_context="logistics"
)

print(f"基础设施: {result.infrastructure}")
print(f"机动走廊: {result.movement_corridors}")
```

## 技术实现

### 核心技术
- **AI视觉分析** - 使用大语言模型的视觉能力分析地形图图片
- **智能提示工程** - 根据分析重点和任务背景动态构建分析提示词
- **结构化输出** - 将AI分析结果结构化为标准格式
- **错误处理** - 完善的异常处理和降级机制

### 工作流程
1. **图片验证** - 检查图片文件是否存在
2. **提示词构建** - 根据参数构建专业的分析提示词
3. **AI分析** - 调用视觉模型分析地形图图片
4. **结果解析** - 解析AI输出并结构化
5. **质量保证** - 确保所有必需字段都存在

## 注意事项

### 使用限制
- 支持的图片格式：PNG, JPG, JPEG
- 建议使用高分辨率图片以获得更好的分析效果
- 需要配置支持视觉功能的AI模型

### 安全提醒
- 本工具仅用于教育和研究目的
- 实际军事应用需要专业人员验证
- 分析结果应结合实地勘察进行确认
- 请遵守相关法律法规和安全规定

### 性能优化
- 大图片可能需要较长的处理时间
- 建议根据实际需求选择合适的分析重点
- 可以通过提供地图比例尺信息提高分析准确性

## 扩展开发

### 自定义分析重点
可以通过修改 `_build_analysis_prompt` 方法来添加新的分析重点：

```python
def _build_analysis_prompt(self, analysis_focus, mission_context, scale_reference):
    # 添加自定义分析重点逻辑
    if analysis_focus == "custom_focus":
        base_prompt += "\n**自定义分析重点描述**"
    return base_prompt
```

### 结果后处理
可以通过重写 `_structure_analysis_result` 方法来自定义结果处理逻辑：

```python
def _structure_analysis_result(self, ai_result, analysis_focus, mission_context):
    # 自定义结果处理逻辑
    return structured_result
```

## 相关工具

- `MilitaryMapAnalyzer` - 基于文本描述的军事地图分析工具
- `DeepAnalyzerTool` - 通用深度分析工具
- `IntelligenceAnalyzer` - 情报分析工具

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本地形图图片分析功能
- 提供多种分析重点和任务背景选项
- 完整的错误处理和结果结构化 