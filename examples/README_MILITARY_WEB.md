# 军事参谋智能体Web系统

## 🎖️ 系统概述

军事参谋智能体Web系统是基于DeepResearchAgent框架构建的专业军事作战方案制定平台。系统采用分层多智能体架构，通过Web界面为用户提供直观的军事任务分析和作战方案制定服务。

## 🏗️ 系统架构

### 核心智能体
- **军事参谋长** (`military_chief_of_staff_agent`): 统筹协调，制定整体作战方案
- **情报分析专家** (`intelligence_analyst_agent`): 分析敌我态势和威胁评估
- **作战规划专家** (`operations_planning_agent`): 制定详细战术和作战计划
- **地图分析专家** (`map_analysis_agent`): 分析地形地貌和地理优势
- **后勤保障专家** (`logistics_agent`): 规划后勤补给和保障方案

### Web界面特性
- 🌐 **现代化Web界面**: 基于Gradio构建，响应式设计
- 📝 **任务输入**: 支持详细的军事任务描述输入
- 🗺️ **地形图上传**: 支持上传地形图、卫星图等辅助分析
- 📊 **实时日志**: 显示分析过程和各智能体的工作状态
- 📋 **方案输出**: 生成详细的军事作战部署方案
- 🎯 **预设示例**: 提供多种典型军事场景模板

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
# OPENAI_API_KEY=your_openai_key
# ANTHROPIC_API_KEY=your_anthropic_key
# GOOGLE_API_KEY=your_google_key
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
# 使用启动脚本（推荐）
cd examples
./start_military_web.sh

# 或直接运行
python examples/military_web_app_enhanced.py
```

5. **访问Web界面**
- 打开浏览器访问: http://localhost:7860
- 系统会自动打开浏览器窗口

## 📖 使用指南

### 1. 系统初始化
- 首次使用需要点击"🚀 初始化系统"按钮
- 系统将加载配置、初始化模型和创建智能体
- 初始化过程可能需要1-2分钟

### 2. 任务输入
在"军事任务描述"框中输入详细的任务信息，建议包括：

```
🎯 任务背景和目标
🗺️ 地形情况描述  
👥 我方兵力配置
⚔️ 敌方情况分析
📋 特殊要求和约束条件
⏰ 时间限制
```

### 3. 地形图上传（可选）
- 支持格式：PNG, JPG, JPEG
- 建议尺寸：800x600以上
- 文件大小：< 10MB
- 内容：地形图、卫星图、作战地图等

### 4. 开始分析
- 点击"🎯 开始分析"按钮
- 系统将调用各专业智能体进行分析
- 可在"分析日志"中查看实时进度
- 分析时间根据任务复杂度为2-10分钟

### 5. 查看结果
- 在"详细作战部署方案"中查看最终结果
- 方案包括态势分析、作战计划、兵力部署等

## 🎯 预设任务示例

系统提供4个典型军事场景：

### 🏔️ 山地防御作战
- 场景：敌方装甲师向战略要地推进
- 重点：利用地形优势进行防御
- 特点：山地地形、制高点控制

### 🏙️ 城市攻坚作战  
- 场景：夺取敌方控制的重要城市
- 重点：减少平民伤亡，保护基础设施
- 特点：城市环境、巷战战术

### 🌊 海岸登陆作战
- 场景：两栖登陆夺取沿海港口
- 重点：建立滩头阵地，快速推进
- 特点：海陆协同、时间窗口

### 🚁 空降突击作战
- 场景：空降夺取敌方后方机场
- 重点：快速夺取，坚守待援
- 特点：垂直突击、孤军深入

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

## 🔧 故障排除

### 常见问题

1. **系统初始化失败**
   - 检查API密钥配置
   - 确认网络连接正常
   - 查看日志文件获取详细错误信息

2. **分析过程中断**
   - 检查API配额是否充足
   - 确认模型服务可用性
   - 重新初始化系统后重试

3. **地形图上传失败**
   - 检查图片格式和大小
   - 确认workdir目录权限
   - 尝试使用其他图片

4. **Web界面无法访问**
   - 检查端口7860是否被占用
   - 确认防火墙设置
   - 尝试使用其他端口

### 日志查看
```bash
# 查看系统日志
tail -f log.txt

# 查看详细错误
python examples/military_web_app_enhanced.py --debug
```

## 📊 性能优化

### 系统要求
- **最低配置**: 4GB RAM, 2核CPU
- **推荐配置**: 8GB+ RAM, 4核+ CPU
- **网络**: 稳定的互联网连接

### 优化建议
1. 使用SSD存储提升I/O性能
2. 配置本地代理减少网络延迟
3. 调整并发数量平衡性能和资源使用
4. 定期清理工作目录和日志文件

## 🔒 安全注意事项

1. **API密钥安全**
   - 不要在代码中硬编码API密钥
   - 定期轮换API密钥
   - 限制API密钥权限

2. **数据安全**
   - 敏感军事信息请谨慎处理
   - 定期清理临时文件
   - 考虑使用本地部署的模型

3. **网络安全**
   - 在内网环境中部署
   - 配置适当的访问控制
   - 使用HTTPS加密传输

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进系统：

1. Fork项目仓库
2. 创建功能分支
3. 提交代码更改
4. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 📞 技术支持

如有问题或建议，请通过以下方式联系：

- 提交GitHub Issue
- 发送邮件至技术支持团队
- 查看项目文档和FAQ

---

**⚠️ 免责声明**: 本系统仅用于学术研究和技术演示，不应用于实际军事行动。使用者需对使用后果承担责任。 