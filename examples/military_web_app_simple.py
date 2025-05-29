#!/usr/bin/env python3
"""
军事参谋智能体系统 Web 界面 - 简化版本
支持实时进度显示
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

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import config
from src.models import model_manager
from src.agent import create_agent
from src.logger import logger
from src.memory import ActionStep, PlanningStep, FinalAnswerStep

class MilitaryWebApp:
    """军事参谋Web应用类 - 简化版"""
    
    def __init__(self):
        self.military_chief = None
        self.current_logs = []
        self.is_running = False
        self.progress_queue = queue.Queue()
        
    async def initialize_system(self):
        """初始化军事参谋系统"""
        try:
            config.init_config("configs/military_config.toml")
            logger.init_logger(config.log_path)
            model_manager.init_models()
            self.military_chief = create_agent()
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
    
    def create_step_callback(self):
        """创建智能体步骤回调函数"""
        def step_callback(step, agent=None):
            """智能体步骤回调函数"""
            try:
                if isinstance(step, ActionStep):
                    if hasattr(step, 'step_number') and step.step_number:
                        message = f"🔄 执行步骤 {step.step_number}"
                        
                        # 根据步骤内容生成更详细的进度信息
                        if hasattr(step, 'model_output') and step.model_output:
                            output_str = str(step.model_output)
                            if "final_answer" in output_str:
                                message = f"✅ 步骤 {step.step_number}: 正在生成最终作战方案"
                            elif "调用工具" in output_str or "Calling tool" in output_str or "call tool" in output_str.lower():
                                # 尝试提取工具名称
                                if "intelligence_analyst_agent" in output_str:
                                    message = f"🔍 步骤 {step.step_number}: 咨询情报分析专家"
                                elif "operations_planning_agent" in output_str:
                                    message = f"⚔️ 步骤 {step.step_number}: 咨询作战规划专家"
                                elif "map_analysis_agent" in output_str:
                                    message = f"🗺️ 步骤 {step.step_number}: 咨询地图分析专家"
                                elif "logistics_agent" in output_str:
                                    message = f"📦 步骤 {step.step_number}: 咨询后勤保障专家"
                                elif "planning" in output_str:
                                    message = f"📋 步骤 {step.step_number}: 更新任务计划"
                                else:
                                    message = f"🛠️ 步骤 {step.step_number}: 正在调用专业工具"
                            else:
                                message = f"🤔 步骤 {step.step_number}: 正在分析和规划"
                        
                        # 检查是否有有用的观察结果（特别是planning工具的输出）
                        if hasattr(step, 'observations') and step.observations:
                            obs = str(step.observations)
                            
                            # 检查是否是planning工具的进度更新
                            if "Progress:" in obs and "steps completed" in obs and "Status:" in obs:
                                # 提取并格式化进度信息
                                formatted_progress = self.format_planning_progress(obs)
                                if formatted_progress:
                                    self.progress_queue.put(formatted_progress)
                                    return  # 已经添加了格式化的进度信息，不需要重复
                            
                            # 对于其他类型的观察结果，提供简要预览
                            obs_preview = obs[:100]
                            if len(obs) > 100:
                                obs_preview += "..."
                            message += f"\n📝 收到反馈: {obs_preview}"
                        
                        self.progress_queue.put(message)
                        
                elif isinstance(step, PlanningStep):
                    message = "📋 正在制定整体作战计划..."
                    if hasattr(step, 'plan') and step.plan:
                        plan_preview = str(step.plan)[:80]
                        message += f"\n计划要点: {plan_preview}..."
                    self.progress_queue.put(message)
                    
                elif isinstance(step, FinalAnswerStep):
                    self.progress_queue.put("🎯 作战方案制定完成！")
                    
            except Exception as e:
                logger.error(f"步骤回调错误: {e}")
        
        return step_callback
    
    def format_planning_progress(self, planning_output: str) -> str:
        """格式化planning工具的进度输出"""
        try:
            lines = planning_output.strip().split('\n')
            
            # 查找关键信息行
            progress_line = ""
            status_line = ""
            steps_start_idx = -1
            
            for i, line in enumerate(lines):
                if line.startswith("Progress:"):
                    progress_line = line
                elif line.startswith("Status:"):
                    status_line = line
                elif line.strip() == "Steps:":
                    steps_start_idx = i + 1
                    break
            
            if not progress_line or not status_line or steps_start_idx == -1:
                return ""  # 无法解析的格式
            
            # 构建格式化的进度显示
            formatted = "📊 **作战计划执行进度**\n\n"
            formatted += f"🎯 {progress_line}\n"
            formatted += f"📈 {status_line}\n\n"
            formatted += "**任务执行状态:**\n"
            
            # 解析步骤信息
            for i in range(steps_start_idx, len(lines)):
                line = lines[i].strip()
                if not line:
                    continue
                
                # 跳过Notes行
                if line.startswith("Notes:"):
                    continue
                
                # 解析步骤行格式: "0. [✓] 步骤描述"
                # 使用正则表达式匹配数字和状态符号
                import re
                match = re.match(r'(\d+)\.\s*\[([✓→!\s]*)\]\s*(.*)', line)
                if match:
                    step_num, status_symbol, description = match.groups()
                    
                    # 映射状态符号到更友好的显示
                    if "✓" in status_symbol:
                        status_emoji = "✅"
                        status_text = "已完成"
                    elif "→" in status_symbol:
                        status_emoji = "🔄"
                        status_text = "进行中"
                    elif "!" in status_symbol:
                        status_emoji = "⚠️"
                        status_text = "受阻"
                    else:  # 空白或其他
                        status_emoji = "⏳"
                        status_text = "待开始"
                    
                    formatted += f"{status_emoji} **{status_text}**: {description}\n"
            
            return formatted
            
        except Exception as e:
            logger.error(f"格式化planning进度时出错: {e}")
            return ""
    
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
            
            # 步骤4：启动智能体分析
            yield self.add_log("🧠 军事参谋长开始分析任务"), ""
            await asyncio.sleep(0.3)
            
            # 添加步骤回调到智能体
            step_callback = self.create_step_callback()
            if not hasattr(self.military_chief, 'step_callbacks'):
                self.military_chief.step_callbacks = []
            self.military_chief.step_callbacks.append(step_callback)
            
            yield self.add_log("👥 正在协调各专业军事智能体..."), ""
            
            # 执行智能体分析 - 简化为标准调用方式
            result = ""
            
            # 启动智能体分析并监控进度
            analysis_task = asyncio.create_task(self.military_chief(full_task))
            
            # 监控实际进度，不再使用模拟进度
            last_progress_time = time.time()
            while not analysis_task.done():
                # 检查进度队列中的实际更新
                progress_updated = False
                while not self.progress_queue.empty():
                    try:
                        progress_msg = self.progress_queue.get_nowait()
                        yield self.add_log(progress_msg), ""
                        progress_updated = True
                        last_progress_time = time.time()
                    except queue.Empty:
                        break
                
                # 如果长时间没有进度更新，显示等待信息
                if not progress_updated and time.time() - last_progress_time > 10:
                    yield self.add_log("⏳ 智能体正在深度分析中，请耐心等待..."), ""
                    last_progress_time = time.time()
                
                # 等待一段时间再检查
                await asyncio.sleep(1)
            
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
            
            # 移除回调
            if step_callback in self.military_chief.step_callbacks:
                self.military_chief.step_callbacks.remove(step_callback)
            
        except Exception as e:
            error_msg = f"❌ 分析失败: {str(e)}"
            yield self.add_log(error_msg), error_msg
            logger.error(f"军事任务分析失败: {e}")
        finally:
            self.is_running = False

    def extract_final_answer(self, result) -> str:
        """提取并清理智能体响应中的final_answer内容"""
        if not result:
            return "未获得响应结果"
        
        # 将结果转换为字符串
        result_str = str(result)
        
        # 查找final_answer内容 - 首先检查是否是字典格式且包含answer
        if isinstance(result, dict) and 'answer' in result:
            return result['answer']
        
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
        
        # 预设任务示例
        with gr.Row():
            gr.Markdown("## 🎯 快速开始示例")
        with gr.Row():
            example_1 = gr.Button("山地防御作战", variant="secondary")
            example_2 = gr.Button("城市攻坚作战", variant="secondary")
            example_3 = gr.Button("海岸登陆作战", variant="secondary")
        
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
        server_port=7860,
        share=False,
        debug=True,
        show_error=True,
        inbrowser=True
    )

if __name__ == "__main__":
    main() 