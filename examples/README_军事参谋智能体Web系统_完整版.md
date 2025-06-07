# 军事参谋智能体Web系统 - 完整使用指南

## 🎖️ 系统概述

军事参谋智能体Web系统是基于DeepResearchAgent框架构建的专业军事作战方案制定平台。系统采用分层多智能体架构，通过现代化Web界面为用户提供直观的军事任务分析和作战方案制定服务。

**当前版本：日志监控版本（`military_web_app_simple.py`）**

## 🏗️ 系统架构

### 核心智能体
- **军事参谋长** (`military_chief`): 统筹协调，制定整体作战方案
- **情报分析专家**: 分析敌我态势和威胁评估
- **作战规划专家**: 制定详细战术和作战计划
- **地图分析专家**: 分析地形地貌和地理优势
- **后勤保障专家**: 规划后勤补给和保障方案

### 核心技术特性
- 🌐 **现代化Web界面**: 基于Gradio构建，响应式设计
- 📝 **任务输入**: 支持详细的军事任务描述输入
- 🗺️ **地形图上传**: 支持上传地形图、卫星图等辅助分析
- 📊 **实时日志监控**: 通过监听日志文件实时显示分析进度
- 📋 **方案输出**: 生成详细的军事作战部署方案
- 🎯 **预设示例**: 提供多种典型军事场景模板

## ✨ 技术亮点 - 日志监控版本

### 🔄 进度监控机制重构
**原机制 → 新机制**
- ❌ Agent回调机制 → ✅ 日志文件监控
- ❌ 步骤回调函数 → ✅ 实时文件监听
- ❌ 内存状态管理 → ✅ 文件IO状态跟踪

### 📊 LogFileMonitor类 - 核心组件
```python
class LogFileMonitor:
    def __init__(self, log_file_path: str)  # 初始化监控器
    def start_monitoring(self)             # 开始监控
    def stop_monitoring(self)              # 停止监控
    def get_new_logs(self) -> list         # 获取新的日志条目
    def _format_log_line(self, line)       # 格式化日志内容
    def _get_emoji_for_log(self, content)  # 智能添加emoji
```

### 🎨 智能日志识别系统
系统能够识别不同类型的日志内容并添加相应图标：

| 日志类型 | Emoji | 触发词 |
|---------|--------|--------|
| 开始操作 | 🚀 | 开始、start |
| 完成操作 | ✅ | 完成、finish、completed |
| 分析过程 | 🔍 | 分析、analyz |
| 规划过程 | 📋 | 规划、planning |
| 情报相关 | 🕵️ | 情报、intelligence |
| 作战相关 | ⚔️ | 作战、operation |
| 地图分析 | 🗺️ | 地图、map |
| 后勤保障 | 📦 | 后勤、logistics |
| 步骤执行 | 🔄 | 步骤、step |
| 错误信息 | ❌ | 错误、error |
| 警告信息 | ⚠️ | 警告、warning |
| 最终结果 | 🎯 | 最终、final |

## 🚀 快速开始

### 环境要求
- Python 3.11+
- 8GB+ RAM
- 网络连接（用于API调用）

### 安装步骤

1. **克隆项目**
```bash
git clone <repository_url>
cd DeepResearchAgent
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置以下API密钥：
PYTHONWARNINGS=ignore
ANONYMIZED_TELEMETRY=false
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_BASE=https://api.anthropic.com
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_APPLICATION_CREDENTIALS=path_to_credentials
GOOGLE_API_BASE=https://generativelanguage.googleapis.com
GOOGLE_API_KEY=your_google_key
```

3. **安装依赖**
```bash
# 使用Poetry（推荐）
make install

# 或使用pip
pip install -r requirements.txt
pip install gradio>=5.0.0
```

4. **启动Web应用**
```bash
cd examples
python military_web_app_simple.py
```

5. **访问Web界面**
- 系统自动在端口19085启动：http://localhost:19085
- 系统会自动打开浏览器窗口

## 📖 详细使用指南

### 1. 系统初始化
- 首次使用需要点击"🚀 初始化系统"按钮
- 系统将加载配置、初始化模型和创建智能体
- **新特性**：支持自动初始化 - 如果开始分析时检测到智能体未初始化，会自动进行初始化
- 初始化过程可能需要1-2分钟

### 2. 任务输入
在"军事任务描述"框中输入详细的任务信息，建议包括：

```
🎯 任务背景和目标：[详细描述作战背景和预期达成的目标]
🗺️ 地形情况描述：[地形特点、关键地标、道路情况等]  
👥 我方兵力配置：[部队规模、装备情况、战斗力评估]
⚔️ 敌方情况分析：[敌军数量、装备、部署位置、战术特点]
📋 特殊要求和约束条件：[时间限制、作战规则、政治考虑等]
⏰ 时间限制：[作战时间窗口、紧急程度]
```

### 3. 地形图上传（可选）
- 支持格式：PNG, JPG, JPEG
- 建议尺寸：800x600以上
- 文件大小：< 10MB
- 内容：地形图、卫星图、作战地图等
- **处理机制**：自动保存到workdir并整合到任务描述中

### 4. 开始分析
- 点击"🎯 开始分析"按钮
- 系统将启动日志监控器，监听：`/eightT/DeepResearchAgent/workdir/military_staff_system/log.txt`
- 可在"实时分析过程"中查看详细的进度信息
- 分析时间根据任务复杂度为2-10分钟

### 5. 实时进度监控
**新版本核心特性 - 实时日志显示**

分析过程中你会看到类似这样的实时进度：

```
[14:45:45] 🚀 开始军事任务分析
[14:45:46] 🗺️ 正在处理地形图...
[14:45:47] ✅ 地形图处理完成
[14:45:48] 📊 地形信息已整合到任务描述
[14:45:49] 👁️ 开始监控智能体日志
[14:45:50] 🧠 军事参谋长开始分析任务
[14:45:51] 👥 正在协调各专业军事智能体...
[14:45:55] 🔍 正在分析任务需求...
[14:45:58] 📋 制定初步作战计划...
[14:46:02] 👥 协调情报分析专家...
[14:46:05] ⚔️ 咨询作战规划专家...
[14:46:10] 🗺️ 进行地形分析评估...
[14:46:15] 📦 规划后勤保障方案...
[14:46:20] 🔄 整合各专家建议...
[14:46:25] ✏️ 生成最终作战方案...
[14:46:30] 🎯 军事方案制定完成！
```

### 6. 查看结果
- 在"作战方案输出"中查看最终结果
- 系统会自动提取并清理智能体响应中的final_answer内容
- 方案包括态势分析、作战计划、兵力部署、风险评估等

## 🎯 预设任务示例

系统提供3个典型军事场景：

### 🏔️ 山地防御作战
**场景描述**：
```
任务背景：敌方装甲师正向我方控制的战略要地推进，预计48小时内到达。

地形情况：目标地区为山地地形，海拔800-1200米，有三个主要制高点，
主要通道为两条山谷道路，地形复杂，植被茂密，有一条河流穿过中央谷地。

我方兵力：一个加强步兵旅，约3500人，配备：
- 反坦克导弹连2个
- 120mm迫击炮营1个  
- 防空导弹连1个
- 工兵连1个
- 侦察连1个

敌方情况：一个机械化师，约8000人，装备：
- 主战坦克60辆（T-80型）
- 步兵战车120辆
- 自行火炮24门
- 武装直升机8架

任务目标：制定防御作战方案，阻止敌方推进，保卫战略要地至少72小时。
```

### 🏙️ 城市攻坚作战  
**场景描述**：
```
任务背景：需要夺取敌方控制的重要城市，该城市是敌方的后勤补给中心。

地形情况：目标城市位于平原地区，面积约50平方公里，城区建筑密集，
有工业区、居民区和商业区，外围有环城公路，市内道路网发达。

我方兵力：一个合成旅，约4000人，装备：
- 主战坦克40辆
- 步兵战车60辆
- 装甲营1个
- 机械化步兵营2个
- 炮兵营1个
- 工兵连1个

敌方情况：一个守备团，约2000人，在城市关键点位构筑了防御工事。

任务目标：制定城市攻坚作战方案，快速夺取城市，减少平民伤亡。
```

### 🌊 海岸登陆作战
**场景描述**：
```
任务背景：执行两栖登陆作战，夺取敌方控制的沿海重要港口。

地形情况：目标海岸线长约5公里，西段为沙滩地形，东段为岩石海岸，
内陆为丘陵地带，港口设施完整，有3个主要码头。

我方兵力：一个海军陆战旅，约3500人，装备：
- 两栖装甲车30辆
- 登陆艇12艘
- 攻击直升机6架
- 两栖突击车40辆

敌方情况：一个海防团，约1500人，在海岸线构筑了三道防线。

任务目标：制定两栖登陆作战方案，快速夺取港口，建立稳固的滩头阵地。
```

## ⚙️ 配置说明

### 主要配置文件
- `configs/military_config.toml`: 军事智能体配置
- `.env`: API密钥和环境变量
- `src/agent/*/prompts/*.yaml`: 智能体提示词模板

### 关键配置项
```toml
[agent]
use_hierarchical_agent = true
use_military_system = true

[agent.military_chief_of_staff_agent_config]
model_id = "claude37-sonnet-thinking"
max_steps = 30
managed_agents = ["intelligence_analyst_agent", "operations_planning_agent", "map_analysis_agent", "logistics_agent"]
```

### 日志监控配置
- **日志文件路径**：`/eightT/DeepResearchAgent/workdir/military_staff_system/log.txt`
- **监控间隔**：0.5秒
- **文件编码**：UTF-8
- **监控模式**：后台线程，非阻塞

## 🔧 技术实现细节

### 异步架构
```python
class MilitaryWebApp:
    async def analyze_military_task(self, task_description, terrain_image):
        # 启动智能体分析
        analysis_task = asyncio.create_task(self.military_chief(full_task))
        
        # 监控日志文件实时进度
        while not analysis_task.done():
            if self.log_monitor:
                new_logs = self.log_monitor.get_new_logs()
                for log_entry in new_logs:
                    yield log_entry  # 流式输出
            await asyncio.sleep(0.8)
```

### 流式输出实现
- 使用异步生成器 `async def` + `yield`
- Gradio流式接口支持实时更新
- 正确处理异步生成器的生命周期

### 智能结果提取
```python
def extract_final_answer(self, result) -> str:
    """智能提取并清理智能体响应中的final_answer内容"""
    # 支持多种格式的结果解析：
    # 1. 字典格式：{'answer': '...'}
    # 2. 嵌套格式：包含军事参谋长报告
    # 3. 转义字符处理
    # 4. 摘要内容过滤
```

### 错误处理机制
- 自动智能体初始化检测
- API调用异常处理
- 文件操作容错
- 用户友好的错误提示

## 🔍 故障排除

### 常见问题及解决方案

1. **系统初始化失败**
   ```
   ❌ 系统初始化失败: 配置文件不存在
   ```
   **解决方案**：
   - 检查 `configs/military_config.toml` 文件是否存在
   - 确认API密钥配置正确
   - 检查网络连接

2. **日志监控不工作**
   ```
   ⚠️ 日志文件监控异常
   ```
   **解决方案**：
   - 检查日志文件路径：`/eightT/DeepResearchAgent/workdir/military_staff_system/log.txt`
   - 确认文件读取权限
   - 验证文件编码为UTF-8

3. **智能体分析失败**
   ```
   ❌ 智能体分析失败: API调用错误
   ```
   **解决方案**：
   - 检查API密钥和配额
   - 确认模型服务可用性
   - 重新初始化系统

4. **地形图上传失败**
   ```
   ❌ 地形图处理失败: 文件保存错误
   ```
   **解决方案**：
   - 检查图片格式（支持PNG/JPG/JPEG）
   - 确认文件大小 < 10MB
   - 检查workdir目录权限

5. **Web界面无法访问**
   ```
   ConnectionError: 无法连接到服务器
   ```
   **解决方案**：
   - 检查端口19085是否被占用
   - 确认防火墙设置
   - 尝试更换端口号

### 调试工具

**日志查看**：
```bash
# 实时查看系统日志
tail -f /eightT/DeepResearchAgent/workdir/military_staff_system/log.txt

# 查看详细错误
python examples/military_web_app_simple.py --debug
```

**环境测试**：
```bash
# 运行系统测试（如果存在）
python examples/test_military_web.py

# 检查依赖
pip list | grep gradio
pip list | grep litellm
```

## 📊 性能优化

### 系统要求
- **最低配置**: 4GB RAM, 2核CPU
- **推荐配置**: 8GB+ RAM, 4核+ CPU  
- **网络**: 稳定的互联网连接

### 优化建议
1. **启动优化**
   - 使用SSD存储提升I/O性能
   - 配置本地代理减少网络延迟
   - 预热智能体减少首次调用时间

2. **运行优化**
   - 调整日志监控间隔（默认0.5秒）
   - 限制日志文件大小，定期轮转
   - 使用队列缓存减少内存占用

3. **界面优化**
   - 启用Gradio缓存机制
   - 优化CSS加载
   - 减少不必要的界面更新

## 🔒 安全注意事项

### API密钥安全
- ✅ 使用环境变量存储密钥
- ✅ 不在代码中硬编码密钥
- ✅ 支持多种API提供商
- ⚠️ 定期轮换API密钥
- ⚠️ 限制API密钥权限

### 数据安全
- ✅ 本地文件存储
- ✅ 临时文件自动清理
- ⚠️ 敏感军事信息请谨慎处理
- ⚠️ 考虑使用本地部署的模型

### 运行安全
- ✅ 日志文件访问控制
- ✅ 工作目录权限管理
- ⚠️ 在内网环境中部署
- ⚠️ 配置适当的防火墙规则


## 🚀 快速启动检查清单

开始使用前，请确认：

- [ ] Python 3.11+ 已安装
- [ ] 依赖包已安装（包括 gradio>=5.0.0）
- [ ] API密钥已配置到 `.env` 文件
- [ ] `configs/military_config.toml` 配置文件存在
- [ ] 端口19085未被占用
- [ ] 网络连接正常
- [ ] 日志目录权限正确

**启动命令**：
```bash
cd examples
python military_web_app_simple.py
```

**访问地址**：http://localhost:19085

## 🤝 贡献指南

欢迎提交改进建议和错误报告！

### 贡献流程
1. Fork项目仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交代码更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

### 开发规范
- 遵循Python PEP 8代码规范
- 添加适当的注释和文档
- 编写单元测试
- 确保向后兼容性

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 📞 技术支持

如有问题或建议，请通过以下方式联系：

- 📧 **GitHub Issues**：提交技术问题和功能请求
- 📖 **项目文档**：查看详细的API文档和教程
- 💬 **社区论坛**：与其他用户交流使用经验

---

## ⚠️ 重要声明

**本系统仅用于学术研究和技术演示目的。**

- 🔬 **学术用途**：支持军事科学研究和教学
- 🎯 **技术展示**：演示AI多智能体协作能力
- ❌ **禁止实际军事应用**：不得用于真实的军事行动
- ⚖️ **用户责任**：使用者需对使用后果承担责任

**系统设计初衷是为了推进人工智能技术在复杂决策支持领域的应用研究，促进相关技术的学术交流与发展。**

---

*最后更新时间：2024年12月 | 文档版本：v3.0* 