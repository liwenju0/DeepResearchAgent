# 军事参谋智能体系统使用指南

## 系统概述

军事参谋智能体系统是一个专门为军事作战规划设计的分层多智能体系统。该系统模拟真实的军事参谋部门结构，能够接收军事任务目标，通过多个专业智能体的协作，生成完整的作战部署方案。

## 系统架构

### 分层结构
```
军事参谋长 (Military Chief of Staff Agent)
├── 情报分析专家 (Intelligence Analyst Agent)
├── 作战规划专家 (Operations Planning Agent)  
├── 地图分析专家 (Map Analysis Agent)
└── 后勤保障专家 (Logistics Agent)
```

### 智能体职责

#### 🎖️ 军事参谋长 (Military Chief of Staff Agent)
- **职责**: 顶层协调和决策
- **功能**: 
  - 分析军事任务目标
  - 协调各专业智能体
  - 整合各部门建议
  - 输出最终作战部署方案

#### 🔍 情报分析专家 (Intelligence Analyst Agent)
- **职责**: 情报收集与分析
- **功能**:
  - 分析敌方兵力部署
  - 评估威胁等级
  - 识别敌方弱点
  - 提供情报评估报告

#### ⚔️ 作战规划专家 (Operations Planning Agent)
- **职责**: 作战方案制定
- **功能**:
  - 制定战术计划
  - 规划兵力部署
  - 设计作战序列
  - 制定应急预案

#### 🗺️ 地图分析专家 (Map Analysis Agent)
- **职责**: 地形地图分析
- **功能**:
  - 分析地形特征
  - 评估地形军事价值
  - 规划行进路线
  - 提供地形利用建议

#### 📦 后勤保障专家 (Logistics Agent)
- **职责**: 后勤支援规划
- **功能**:
  - 评估后勤需求
  - 规划补给线路
  - 协调运输储存
  - 确保作战持续性

## 专用工具

### 🛠️ 军事地图分析工具 (Military Map Analyzer)
- 分析地形地貌特征
- 评估地形军事价值
- 识别关键地形要点
- 推荐行进路线
- 提供战术建议

### 🛠️ 情报分析工具 (Intelligence Analyzer)
- 分析敌方兵力部署
- 评估威胁等级
- 识别装备能力
- 发现战术弱点
- 提供应对建议

## 快速开始

### 1. 环境配置

确保已安装所有依赖：
```bash
# 使用Poetry安装
make install

# 或使用requirements.txt
pip install -r requirements.txt
```

配置环境变量（`.env`文件）：
```env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
# 其他必要的API密钥
```

### 2. 使用军事配置

使用预配置的军事系统配置文件：
```python
from src.config import config
from src.agent import create_agent

# 初始化军事配置
config.init_config("configs/military_config.toml")

# 创建军事参谋系统
military_chief = create_agent()
```

### 3. 执行军事任务

```python
import asyncio

async def run_military_mission():
    # 定义军事任务
    mission = """
    任务背景：敌方装甲师正向我方控制的战略要地推进。
    
    地形情况：目标地区为山地地形，有多个制高点，主要通道为两条山谷道路。
    
    我方兵力：一个加强步兵旅，配备反坦克武器、迫击炮和防空武器。
    
    敌方情况：一个机械化师，约8000人，装备主战坦克60辆，装甲车120辆。
    
    任务目标：制定防御作战方案，阻止敌方推进，保卫战略要地。
    """
    
    # 执行任务规划
    result = await military_chief(mission)
    print("作战部署方案：", result)

# 运行任务
asyncio.run(run_military_mission())
```

### 4. 运行示例

直接运行预配置的示例：
```bash
python examples/run_military_example.py
```

## 配置说明

### 军事系统配置 (military_config.toml)

```toml
[agent]
name = "military_staff_system"
use_hierarchical_agent = true
use_military_system = true  # 启用军事系统

# 军事参谋长配置
[agent.military_chief_of_staff_agent_config]
model_id = "claude37-sonnet-thinking"
name = "military_chief_of_staff_agent"
description = "军事参谋长，负责制定和协调军事作战计划"
max_steps = 30
tools = ["military_map_analyzer", "intelligence_analyzer"]
managed_agents = ["intelligence_analyst_agent", "operations_planning_agent", "map_analysis_agent", "logistics_agent"]

# 其他智能体配置...
```

## 使用场景

### 1. 防御作战规划
- 分析敌方进攻态势
- 制定防御部署方案
- 规划防御工事建设
- 安排后勤保障

### 2. 攻击作战规划
- 评估攻击目标
- 制定突破方案
- 规划兵力投送
- 协调各兵种配合

### 3. 地形分析评估
- 分析作战地区地形
- 评估地形军事价值
- 规划最优路线
- 提供地形利用建议

### 4. 情报分析处理
- 收集敌方情报
- 分析威胁等级
- 识别作战机会
- 制定应对措施

## 输出示例

系统会生成包含以下内容的完整作战部署方案：

```
📋 作战部署方案

🎯 作战目标分析
- 主要目标：保卫战略要地
- 成功标准：阻止敌方推进48小时以上

🔍 敌情评估
- 敌方兵力：机械化师约8000人
- 威胁等级：高威胁
- 主要威胁：重型装甲部队

🗺️ 地形分析
- 地形类型：山地
- 关键要点：三个制高点
- 推荐路线：山谷主通道防御

⚔️ 兵力部署
- 主防御阵地：1号高地
- 预备队位置：2号高地后方
- 反坦克阵地：山谷入口

📦 后勤保障
- 弹药储备：3个基数
- 补给路线：后方山路
- 医疗救护：野战医院设置

🚨 风险评估
- 主要风险：敌方空中打击
- 应急预案：防空掩护方案
```

## 扩展开发

### 添加新的军事智能体

1. 创建智能体类：
```python
@register_agent("new_military_agent")
class NewMilitaryAgent(AsyncMultiStepAgent):
    # 实现智能体逻辑
    pass
```

2. 添加配置：
```toml
[agent.new_military_agent_config]
model_id = "claude37-sonnet-thinking"
name = "new_military_agent"
# 其他配置...
```

3. 更新管理关系：
```toml
managed_agents = ["existing_agents", "new_military_agent"]
```

### 添加新的军事工具

1. 创建工具类：
```python
@register_tool("new_military_tool")
class NewMilitaryTool(AsyncTool):
    # 实现工具功能
    pass
```

2. 在智能体配置中添加工具：
```toml
tools = ["existing_tools", "new_military_tool"]
```

## 注意事项

1. **模型选择**: 建议使用高性能模型（如Claude或GPT-4）以确保军事分析的准确性
2. **安全考虑**: 本系统仅用于学术研究和演示，不应用于实际军事行动
3. **数据隐私**: 确保敏感军事信息的安全处理
4. **性能优化**: 大型军事场景可能需要较长处理时间，建议合理设置超时参数

## 故障排除

### 常见问题

1. **智能体注册失败**
   - 检查智能体是否正确注册
   - 确认配置文件路径正确

2. **工具调用失败**
   - 验证工具是否正确注册
   - 检查工具参数格式

3. **配置加载错误**
   - 确认配置文件格式正确
   - 检查路径配置是否存在

### 调试建议

1. 启用详细日志：
```python
from src.logger import LogLevel
# 设置详细日志级别
verbosity_level=LogLevel.DEBUG
```

2. 单步调试：
```python
# 单独测试各个智能体
intelligence_agent = create_single_agent("intelligence_analyst_agent")
result = await intelligence_agent("测试任务")
```

## 贡献指南

欢迎为军事参谋系统贡献代码和改进建议：

1. Fork 项目仓库
2. 创建功能分支
3. 提交代码更改
4. 创建 Pull Request

## 许可证

本项目遵循项目根目录下的 LICENSE 文件中指定的许可证。 