#!/usr/bin/env python3
"""
军事参谋智能体系统 Web 界面 - 简化版本
支持实时进度显示（通过监听日志文件）
"""

import asyncio
import sys
import os
import gradio as gr
import time
from datetime import datetime
from typing import Optional
from PIL import Image
import threading
import queue
import re

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import config
from src.models import model_manager
from src.agent import create_agent
from src.logger import logger

class LogFileMonitor:
    """日志文件监控器"""
    
    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path
        self.last_position = 0
        self.is_monitoring = False
        self.progress_queue = queue.Queue()
        
    def start_monitoring(self):
        """开始监控日志文件"""
        self.is_monitoring = True
        # 获取当前文件位置
        if os.path.exists(self.log_file_path):
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                f.seek(0, 2)  # 移动到文件末尾
                self.last_position = f.tell()
        else:
            self.last_position = 0
            
        # 启动监控线程
        monitor_thread = threading.Thread(target=self._monitor_log_file, daemon=True)
        monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        
    def _monitor_log_file(self):
        """监控日志文件变化"""
        while self.is_monitoring:
            try:
                if os.path.exists(self.log_file_path):
                    with open(self.log_file_path, 'r', encoding='utf-8') as f:
                        f.seek(self.last_position)
                        new_lines = f.readlines()
                        self.last_position = f.tell()
                        
                        for line in new_lines:
                            if line.strip():  # 忽略空行
                                # 格式化日志行并添加到队列
                                formatted_line = self._format_log_line(line.strip())
                                if formatted_line:
                                    self.progress_queue.put(formatted_line)
                
                time.sleep(0.5)  # 每0.5秒检查一次
            except Exception as e:
                # 日志错误不影响监控
                time.sleep(1)
                
    def _format_log_line(self, line: str) -> str:
        line = line.strip()
        """格式化日志行"""
        try:
            # 提取时间戳和日志内容
            if " - " in line and "INFO" in line:
                # 标准日志格式: 2025-05-29 14:45:45 - logger:INFO: logger.py:77 - 内容
                parts = line.split(" - ")
                if len(parts) >= 3:
                    timestamp = parts[0]
                    log_content = " - ".join(parts[3:]) if len(parts) > 3 else parts[2]
                    
                    # 简化时间戳显示
                    try:
                        time_part = timestamp.split()[1] if ' ' in timestamp else timestamp
                        formatted_time = time_part[:8]  # 只显示HH:MM:SS
                    except:
                        formatted_time = timestamp
                    
                    # 智能识别日志内容类型并添加适当的emoji
                    emoji = self._get_emoji_for_log(log_content)
                    
                    return f"**[{formatted_time}]** {emoji} {log_content}"
            if (
                line.startswith("Plan:")
                or line.startswith("Status:")
                or line.startswith("Steps:")
                or line.startswith("0.")
                or line.startswith("1.")
                or line.startswith("2.")
                or line.startswith("3.")
                or line.startswith("4.")
                or line.startswith("5.")
                or line.startswith("6.")
                or line.startswith("7.")
                or line.startswith("8.")
                or line.startswith("9.")
                or line.startswith("Notes:")
            ):
                return line
                    
            return None
        except Exception:
            return None
    
    def _get_emoji_for_log(self, content: str) -> str:
        """根据日志内容获取对应的emoji"""
        content_lower = content.lower()
        
        if "开始" in content or "start" in content_lower:
            return "🚀"
        elif "完成" in content or "finish" in content_lower or "completed" in content_lower:
            return "✅"
        elif "分析" in content or "analyz" in content_lower:
            return "🔍"
        elif "规划" in content or "planning" in content_lower:
            return "📋"
        elif "情报" in content or "intelligence" in content_lower:
            return "🕵️"
        elif "作战" in content or "operation" in content_lower:
            return "⚔️"
        elif "地图" in content or "map" in content_lower:
            return "🗺️"
        elif "后勤" in content or "logistics" in content_lower:
            return "📦"
        elif "步骤" in content or "step" in content_lower:
            return "🔄"
        elif "错误" in content or "error" in content_lower:
            return "❌"
        elif "警告" in content or "warning" in content_lower:
            return "⚠️"
        elif "最终" in content or "final" in content_lower:
            return "🎯"
        else:
            return "📝"
    
    def get_new_logs(self) -> list:
        """获取新的日志条目"""
        logs = []
        while not self.progress_queue.empty():
            try:
                logs.append(self.progress_queue.get_nowait())
            except queue.Empty:
                break
        return logs

class MilitaryWebApp:
    """军事参谋Web应用类 - 简化版"""
    
    def __init__(self):
        self.military_chief = None
        self.current_logs = []
        self.is_running = False
        self.log_monitor = None
        
    async def initialize_system(self):
        """初始化军事参谋系统"""
        try:
            # 获取正确的配置文件路径
            import os
            from dotenv import load_dotenv
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            config_path = os.path.join(project_root, "configs", "military_config.toml")
            
            # 显式加载环境变量
            env_path = os.path.join(project_root, ".env")
            load_dotenv(env_path, verbose=True)
            
            config.init_config(config_path)
            logger.init_logger(config.log_path)
            model_manager.init_models()
            self.military_chief = create_agent()
            
            # 初始化日志监控器
            log_file_path = "/eightT/DeepResearchAgent/workdir/military_staff_system/log.txt"
            self.log_monitor = LogFileMonitor(log_file_path)
            
            return "✅ 军事参谋系统初始化成功"
        except Exception as e:
            logger.error(f"系统初始化失败: {e}")
            return f"❌ 系统初始化失败: {str(e)}"
    
    def add_log(self, message: str):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"**[{timestamp}]** {message}"
        self.current_logs.append(log_entry)
        return "\n\n".join(self.current_logs)
    
    def clear_logs(self):
        """清空日志"""
        self.current_logs = []
        return "等待开始分析..."
    
    def process_terrain_image(self, image: Optional[Image.Image]) -> str:
        """处理上传的地形图"""
        if image is None:
            return "未上传地形图"
        
        try:
            # 保存图片到临时目录
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = f"workdir/terrain_map_{timestamp}.png"
            
            # 确保目录存在
            os.makedirs("workdir", exist_ok=True)
            
            # 保存图片
            image.save(image_path)
            
            # 获取图片信息
            width, height = image.size
            file_size = os.path.getsize(image_path)
            
            return f"✅ 地形图已上传\n📁 路径: {image_path}\n📐 尺寸: {width}x{height}\n📊 大小: {file_size/1024:.1f}KB"
        except Exception as e:
            return f"❌ 地形图处理失败: {str(e)}"
    
    async def analyze_military_task(self, task_description: str, terrain_image: Optional[Image.Image]):
        """分析军事任务"""
        # 检查智能体是否已初始化
        if not self.military_chief:
            yield self.add_log("⚠️ 检测到智能体未初始化，正在自动初始化..."), ""
            try:
                await self.initialize_system()
                yield self.add_log("✅ 智能体自动初始化完成"), ""
            except Exception as e:
                error_msg = f"❌ 智能体初始化失败: {str(e)}"
                yield self.add_log(error_msg), error_msg
                return
        
        self.is_running = True
        self.clear_logs()
        
        try:
            # 步骤1：初始化
            yield self.add_log("🚀 开始军事任务分析"), ""
            await asyncio.sleep(0.3)
            
            # 步骤2：处理地形图
            terrain_info = ""
            if terrain_image:
                yield self.add_log("🗺️ 正在处理地形图..."), ""
                await asyncio.sleep(0.5)
                terrain_info = self.process_terrain_image(terrain_image)
                yield self.add_log("✅ 地形图处理完成"), ""
            
            # 步骤3：准备完整任务描述
            full_task = task_description
            if terrain_info and "✅" in terrain_info:
                full_task += f"\n\n地形图信息：\n{terrain_info}"
                yield self.add_log("📊 地形信息已整合到任务描述"), ""
            
            # 步骤4：启动日志监控
            if self.log_monitor:
                self.log_monitor.start_monitoring()
                yield self.add_log("👁️ 开始监控智能体日志"), ""
            
            # 步骤5：启动智能体分析
            yield self.add_log("🧠 军事参谋长开始分析任务"), ""
            yield self.add_log("👥 正在协调各专业军事智能体..."), ""
            await asyncio.sleep(0.3)
            
            # 执行智能体分析
            result = ""
            
            # 启动智能体分析并监控进度
            analysis_task = asyncio.create_task(self.military_chief(full_task))
            
            # 监控日志文件实时进度
            last_log_time = time.time()
            while not analysis_task.done():
                # 检查日志监控器中的新日志
                if self.log_monitor:
                    new_logs = self.log_monitor.get_new_logs()
                    for log_entry in new_logs:
                        self.current_logs.append(log_entry)
                        yield "\n\n".join(self.current_logs), ""
                        last_log_time = time.time()
                
                # 如果长时间没有日志更新，显示等待信息
                if time.time() - last_log_time > 15:
                    yield self.add_log("⏳ 智能体正在深度分析中，请耐心等待..."), ""
                    last_log_time = time.time()
                
                # 等待一段时间再检查
                await asyncio.sleep(0.8)
            
            # 停止日志监控
            if self.log_monitor:
                self.log_monitor.stop_monitoring()
            
            # 获取最后的日志更新
            if self.log_monitor:
                new_logs = self.log_monitor.get_new_logs()
                for log_entry in new_logs:
                    self.current_logs.append(log_entry)
                    yield "\n\n".join(self.current_logs), ""
            
            # 获取结果
            try:
                result = await analysis_task
                
                # 提取并清理final_answer内容
                clean_result = self.extract_final_answer(result)
                
                yield self.add_log("🎯 军事方案制定完成！"), clean_result
            except Exception as analysis_error:
                error_msg = f"❌ 智能体分析失败: {str(analysis_error)}"
                yield self.add_log(error_msg), error_msg
                logger.error(f"智能体分析错误: {analysis_error}")
            
        except Exception as e:
            error_msg = f"❌ 分析失败: {str(e)}"
            yield self.add_log(error_msg), error_msg
            logger.error(f"军事任务分析失败: {e}")
        finally:
            self.is_running = False
            if self.log_monitor:
                self.log_monitor.stop_monitoring()

    def extract_final_answer(self, result) -> str:
        """提取并清理智能体响应中的final_answer内容"""
        if not result:
            return "未获得响应结果"
        
        # 将结果转换为字符串
        result_str = str(result)
        
        # 查找final_answer内容 - 首先检查是否是字典格式且包含answer
        if isinstance(result, dict) and 'answer' in result:
            return result['answer']

        try:
            result_str = result_str[result_str.find("{"):result_str.find("}")+1]
            import json
            result = json.loads(result_str)
            if 'answer' in result:
                return result['answer']
        except Exception as e:
            logger.error(f"提取final_answer时出错: {e}")
            
        
        # 从字符串中提取answer字段 - 处理复杂的嵌套结构
        import re
        
        # 查找 "以下是您的军事参谋长" 开头的内容
        chief_report_match = re.search(r"以下是您的军事参谋长.*?的最终报告：\s*\{'answer':\s*'(.*?)'(?:\s*}|$)", result_str, re.DOTALL)
        if chief_report_match:
            answer_content = chief_report_match.group(1)
            # 处理转义字符
            answer_content = answer_content.replace("\\'", "'")
            answer_content = answer_content.replace("\\n", "\n")
            answer_content = answer_content.replace("\\\\", "\\")
            return answer_content
        
        # 尝试匹配标准的 {'answer': '...'} 格式
        answer_match = re.search(r"'answer'\s*:\s*'(.*?)'(?:\s*}|$)", result_str, re.DOTALL)
        if answer_match:
            answer_content = answer_match.group(1)
            # 处理转义字符
            answer_content = answer_content.replace("\\'", "'")
            answer_content = answer_content.replace("\\n", "\n")
            answer_content = answer_content.replace("\\\\", "\\")
            
            # 如果内容包含 "For more detail"，则截取之前的内容
            for_more_detail_index = answer_content.find("For more detail, find below a summary")
            if for_more_detail_index != -1:
                answer_content = answer_content[:for_more_detail_index].strip()
            
            return answer_content
        
        # 如果找不到answer字段，检查是否包含"For more detail"，如果有则截取之前的内容
        for_more_detail_index = result_str.find("For more detail, find below a summary of this agent's work:")
        if for_more_detail_index != -1:
            clean_result = result_str[:for_more_detail_index].strip()
            # 移除可能的末尾符号
            if clean_result.endswith("'}"):
                clean_result = clean_result[:-2]
            if clean_result.endswith("'"):
                clean_result = clean_result[:-1]
            return clean_result
        
        # 最后尝试移除summary_of_work部分
        summary_index = result_str.find("<summary_of_work>")
        if summary_index != -1:
            clean_result = result_str[:summary_index].strip()
            return clean_result
        
        # 返回原始结果
        return result_str

# 全局应用实例
app = MilitaryWebApp()

def sync_initialize():
    """同步初始化"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(app.initialize_system())
    finally:
        loop.close()

def analyze_task_streaming(task_description: str, terrain_image: Optional[Image.Image]):
    """流式分析任务"""
    if not task_description.strip():
        yield "❌ 请输入军事任务描述", ""
        return
    
    if not app.military_chief:
        yield "❌ 系统未初始化，请先初始化系统", ""
        return
    
    # 运行异步生成器
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        async def run_analysis():
            async for logs, result in app.analyze_military_task(task_description, terrain_image):
                yield logs, result
        
        # 将异步生成器转换为同步
        async_gen = run_analysis()
        try:
            while True:
                logs, result = loop.run_until_complete(async_gen.__anext__())
                yield logs, result
        except StopAsyncIteration:
            pass
    finally:
        loop.close()

def create_interface():
    """创建Gradio界面"""
    
    # 自定义CSS样式
    custom_css = """
    .military-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    .status-box {
        border: 2px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f8f9fa;
    }
    
    .log-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        padding: 15px;
        font-family: 'Arial', sans-serif;
        max-height: 450px;
        overflow-y: auto;
        font-size: 14px;
        line-height: 1.6;
    }
    
    .log-box h3 {
        color: #1e3c72;
        margin-top: 15px;
        margin-bottom: 10px;
        font-size: 1.1em;
    }
    
    .log-box strong {
        color: #2a5298;
    }
    
    .result-box {
        background-color: #fff;
        border: 2px solid #28a745;
        border-radius: 8px;
        padding: 15px;
        font-family: 'Arial', sans-serif;
        max-height: 500px;
        overflow-y: auto;
        line-height: 1.6;
    }
    
    .result-box h1, .result-box h2, .result-box h3 {
        color: #1e3c72;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    
    .result-box h1 {
        font-size: 1.8em;
        border-bottom: 2px solid #28a745;
        padding-bottom: 5px;
    }
    
    .result-box h2 {
        font-size: 1.5em;
        color: #2a5298;
    }
    
    .result-box h3 {
        font-size: 1.3em;
        color: #495057;
    }
    
    .result-box h4 {
        font-size: 1.1em;
        color: #6c757d;
        margin-top: 15px;
        margin-bottom: 8px;
    }
    
    .result-box ul, .result-box ol {
        margin-left: 20px;
        margin-bottom: 10px;
    }
    
    .result-box li {
        margin-bottom: 5px;
    }
    
    .result-box strong {
        color: #1e3c72;
    }
    
    .result-box code {
        background-color: #f8f9fa;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
    }
    """
    
    with gr.Blocks(css=custom_css, title="军事参谋智能体系统") as interface:
        
        gr.HTML("""
        <div class="military-header">
            <h1>🎖️ 军事参谋智能体系统</h1>
            <p>基于AI的军事作战方案制定与分析平台 - 实时进度版</p>
        </div>
        """)
        
        # 系统状态
        with gr.Row():
            with gr.Column():
                system_status = gr.Textbox(
                    label="🔧 系统状态",
                    value="系统未初始化",
                    interactive=False,
                    elem_classes=["status-box"]
                )
                init_btn = gr.Button("🚀 初始化系统", variant="primary")
         # 预设任务示例
        with gr.Row():
            gr.Markdown("## 🎯 快速开始示例")
        with gr.Row():
            example_1 = gr.Button("山地防御作战", variant="secondary")
            example_2 = gr.Button("城市攻坚作战", variant="secondary")
            example_3 = gr.Button("海岸登陆作战", variant="secondary")
        
        # 主要功能区域
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("## 📝 军事任务输入")
                task_input = gr.Textbox(
                    label="军事任务描述",
                    placeholder="""请详细描述军事任务，包括：
• 任务背景和目标
• 地形情况说明  
• 我方兵力配置
• 敌方情况分析
• 特殊要求或限制

示例：
任务背景：敌方装甲师正向我方控制的战略要地推进，预计48小时内到达。
地形情况：目标地区为山地地形，有三个制高点，主要通道为两条山谷道路。
我方兵力：一个加强步兵旅，配备反坦克武器、迫击炮和防空武器。
敌方情况：一个机械化师，约8000人，装备主战坦克60辆。
任务目标：制定防御作战方案，阻止敌方推进。""",
                    lines=10,
                    max_lines=15
                )
                
                terrain_image = gr.Image(
                    label="🗺️ 地形图上传（可选）",
                    type="pil",
                    height=200
                )
                
                with gr.Row():
                    analyze_btn = gr.Button("🎯 开始分析", variant="primary", size="lg")
                    clear_btn = gr.Button("🗑️ 清空输入", variant="secondary")
            
            with gr.Column(scale=3):
                gr.Markdown("## 📊 实时分析过程")
                analysis_logs = gr.Markdown(
                    value="等待开始分析...",
                    elem_classes=["log-box"]
                )
                
                gr.Markdown("## 📋 作战方案输出")
                result_output = gr.Markdown(
                    value="等待分析结果...",
                    elem_classes=["result-box"]
                )
        
       
        
        # 使用说明
        with gr.Row():
            gr.Markdown("""
            ## 📖 使用说明
            1. **初始化系统**：首次使用前请点击"初始化系统"按钮
            2. **输入任务**：详细描述军事任务，包括背景、地形、兵力等信息
            3. **上传地图**：可选择上传地形图辅助分析
            4. **开始分析**：点击"开始分析"按钮，系统将实时显示处理进度
            5. **查看结果**：分析完成后查看详细的作战部署方案
            
            **注意**：系统会协调多个专业军事智能体进行协作分析，整个过程可能需要1-3分钟。
            """)
        
        # 事件处理函数
        def clear_inputs():
            return "", None, "等待开始分析...", "等待分析结果..."
        
        def load_example_1():
            return """任务背景：敌方装甲师正向我方控制的战略要地推进，预计48小时内到达。

地形情况：目标地区为山地地形，海拔800-1200米，有三个主要制高点，主要通道为两条山谷道路，地形复杂，植被茂密，有一条河流穿过中央谷地。

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
- 具备强大的火力和机动能力

任务目标：制定防御作战方案，阻止敌方推进，保卫战略要地至少72小时，等待后续增援。"""
        
        def load_example_2():
            return """任务背景：需要夺取敌方控制的重要城市，该城市是敌方的后勤补给中心和交通枢纽。

地形情况：目标城市位于平原地区，面积约50平方公里，城区建筑密集，有工业区、居民区和商业区，外围有环城公路，市内道路网发达，有3座桥梁跨越穿城河流。

我方兵力：一个合成旅，约4000人，装备：
- 主战坦克40辆
- 步兵战车60辆
- 装甲营1个
- 机械化步兵营2个
- 炮兵营1个
- 工兵连1个

敌方情况：一个守备团，约2000人，在城市关键点位构筑了防御工事：
- 轻型装甲车20辆
- 反坦克武器若干
- 在桥梁、政府大楼等要点设置了障碍

任务目标：制定城市攻坚作战方案，快速夺取城市，减少平民伤亡，确保关键设施完整。"""
        
        def load_example_3():
            return """任务背景：执行两栖登陆作战，夺取敌方控制的沿海重要港口，建立滩头阵地。

地形情况：目标海岸线长约5公里，西段为沙滩地形，东段为岩石海岸，内陆为丘陵地带，港口设施完整，有3个主要码头，1个机场位于内陆10公里处。

我方兵力：一个海军陆战旅，约3500人，装备：
- 两栖装甲车30辆
- 登陆艇12艘
- 攻击直升机6架
- 两栖突击车40辆
- 海军火力支援

敌方情况：一个海防团，约1500人，防御部署：
- 在海岸线构筑了三道防线
- 配备海防炮8门
- 反舰导弹阵地2个
- 地雷障碍若干

任务目标：制定两栖登陆作战方案，快速夺取港口，建立稳固的滩头阵地，为后续部队登陆创造条件。"""
        
        # 事件绑定
        init_btn.click(
            fn=sync_initialize,
            outputs=[system_status]
        )
        
        # 使用流式输出实现实时进度显示
        analyze_btn.click(
            fn=analyze_task_streaming,
            inputs=[task_input, terrain_image],
            outputs=[analysis_logs, result_output],
            show_progress=True  # 显示进度条
        )
        
        clear_btn.click(
            fn=clear_inputs,
            outputs=[task_input, terrain_image, analysis_logs, result_output]
        )
        
        # 示例按钮绑定
        example_1.click(
            fn=load_example_1,
            outputs=[task_input]
        )
        
        example_2.click(
            fn=load_example_2,
            outputs=[task_input]
        )
        
        example_3.click(
            fn=load_example_3,
            outputs=[task_input]
        )
    
    return interface

def main():
    """主函数"""
    print("🚀 启动军事参谋智能体Web系统 - 简化版")
    print("=" * 60)
    print("✨ 支持实时进度显示")
    print("🔧 自动智能体协调")
    print("📊 详细分析日志")
    print("=" * 60)
    
    # 创建Gradio界面
    interface = create_interface()
    
    # 启动Web服务
    interface.launch(
        server_name="0.0.0.0",
        server_port=19085,
        share=False,
        debug=True,
        show_error=True,
        inbrowser=True
    )

if __name__ == "__main__":
    main() 