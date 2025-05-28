#!/usr/bin/env python3
"""
军事参谋智能体系统 Web 界面 (增强版)

基于Gradio构建的Web应用，提供：
- 军事任务输入界面
- 地形图上传功能
- 实时分析过程展示
- 军事方案输出
- 进度条和状态指示
- 详细的日志记录
"""

import asyncio
import sys
import os
import gradio as gr
import threading
import time
import json
from datetime import datetime
from typing import Optional, List, Tuple, Dict, Any
import base64
from io import BytesIO
from PIL import Image
import queue
import traceback

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import config
from src.models import model_manager
from src.agent import create_agent
from src.logger import logger

class MilitaryWebAppEnhanced:
    """增强版军事参谋Web应用类"""
    
    def __init__(self):
        self.military_chief = None
        self.analysis_logs = []
        self.current_task_id = None
        self.is_analyzing = False
        self.progress_queue = queue.Queue()
        self.system_initialized = False
        
    async def initialize_system(self):
        """初始化军事参谋系统"""
        try:
            self.add_analysis_log("🔧 开始初始化系统...")
            
            # 初始化配置
            config.init_config("configs/military_config.toml")
            self.add_analysis_log("✅ 配置文件加载完成")
            
            # 初始化日志系统
            logger.init_logger(config.log_path)
            self.add_analysis_log("✅ 日志系统初始化完成")
            
            # 初始化模型管理器
            model_manager.init_models()
            self.add_analysis_log("✅ 模型管理器初始化完成")
            
            # 创建军事参谋系统
            self.military_chief = create_agent()
            self.add_analysis_log("✅ 军事参谋智能体创建完成")
            
            self.system_initialized = True
            return "✅ 军事参谋系统初始化成功", "\n".join(self.analysis_logs)
            
        except Exception as e:
            error_msg = f"❌ 系统初始化失败: {str(e)}"
            logger.error(f"系统初始化失败: {e}\n{traceback.format_exc()}")
            self.add_analysis_log(error_msg)
            return error_msg, "\n".join(self.analysis_logs)
    
    def add_analysis_log(self, message: str, log_type: str = "info"):
        """添加分析日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.analysis_logs.append(log_entry)
        
        # 限制日志数量，避免内存溢出
        if len(self.analysis_logs) > 100:
            self.analysis_logs = self.analysis_logs[-50:]
        
        return "\n".join(self.analysis_logs)
    
    def clear_logs(self):
        """清空日志"""
        self.analysis_logs = []
        return ""
    
    def process_terrain_image(self, image: Optional[Image.Image]) -> Tuple[str, str]:
        """处理上传的地形图"""
        if image is None:
            return "未上传地形图", ""
        
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
            
            info_msg = f"✅ 地形图已上传\n📁 路径: {image_path}\n📐 尺寸: {width}x{height}\n📊 大小: {file_size/1024:.1f}KB"
            log_msg = f"🗺️ 地形图处理完成 - 尺寸: {width}x{height}, 大小: {file_size/1024:.1f}KB"
            
            return info_msg, log_msg
            
        except Exception as e:
            error_msg = f"❌ 地形图处理失败: {str(e)}"
            return error_msg, error_msg
    
    async def analyze_military_task_with_progress(
        self, 
        task_description: str, 
        terrain_image: Optional[Image.Image]
    ) -> Tuple[str, str, str]:
        """分析军事任务并提供进度更新"""
        if not self.system_initialized or not self.military_chief:
            return "❌ 系统未初始化，请先初始化系统", "", "系统未就绪"
        
        if not task_description.strip():
            return "❌ 请输入军事任务描述", "", "输入错误"
        
        if self.is_analyzing:
            return "❌ 系统正在分析其他任务，请稍后再试", "", "系统忙碌"
        
        try:
            self.is_analyzing = True
            
            # 生成任务ID
            self.current_task_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 清空之前的日志
            self.clear_logs()
            
            # 添加初始日志
            logs = self.add_analysis_log("🚀 开始军事任务分析")
            logs = self.add_analysis_log(f"📋 任务ID: {self.current_task_id}")
            
            # 处理地形图
            terrain_info = ""
            if terrain_image:
                terrain_info, terrain_log = self.process_terrain_image(terrain_image)
                logs = self.add_analysis_log(terrain_log)
            
            # 构建完整的任务描述
            full_task = task_description
            if terrain_info and "✅" in terrain_info:
                full_task += f"\n\n地形图信息：\n{terrain_info}"
            
            # 添加分析开始日志
            logs = self.add_analysis_log("🧠 军事参谋长开始分析任务...")
            logs = self.add_analysis_log("📊 正在调用各专业智能体...")
            
            # 执行军事任务分析
            result = await self.military_chief(full_task)
            
            # 添加完成日志
            logs = self.add_analysis_log("✅ 军事方案制定完成")
            logs = self.add_analysis_log(f"📝 方案长度: {len(result)} 字符")
            
            return result, logs, "分析完成"
            
        except Exception as e:
            error_msg = f"❌ 军事任务分析失败: {str(e)}"
            logger.error(f"军事任务分析失败: {e}\n{traceback.format_exc()}")
            logs = self.add_analysis_log(error_msg)
            return error_msg, logs, "分析失败"
        
        finally:
            self.is_analyzing = False

# 创建全局应用实例
app = MilitaryWebAppEnhanced()

def sync_initialize():
    """同步初始化函数"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(app.initialize_system())
    finally:
        loop.close()

def sync_analyze_task(task_description: str, terrain_image: Optional[Image.Image]):
    """同步分析任务函数"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            app.analyze_military_task_with_progress(task_description, terrain_image)
        )
    finally:
        loop.close()

def create_enhanced_gradio_interface():
    """创建增强版Gradio界面"""
    
    # 自定义CSS样式
    custom_css = """
    .military-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #1e3c72 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .status-box {
        border: 2px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background: linear-gradient(45deg, #f8f9fa, #ffffff);
    }
    
    .log-box {
        background-color: #1e1e1e;
        color: #00ff00;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 15px;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        max-height: 400px;
        overflow-y: auto;
        line-height: 1.4;
    }
    
    .result-box {
        background-color: #f8f9fa;
        border: 2px solid #28a745;
        border-radius: 10px;
        padding: 15px;
        font-family: 'Arial', sans-serif;
    }
    
    .input-section {
        background: linear-gradient(45deg, #ffffff, #f8f9fa);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    
    .output-section {
        background: linear-gradient(45deg, #f8f9fa, #ffffff);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    """
    
    with gr.Blocks(css=custom_css, title="军事参谋智能体系统 - 增强版") as interface:
        
        # 标题和说明
        gr.HTML("""
        <div class="military-header">
            <h1>🎖️ 军事参谋智能体系统</h1>
            <h3>基于AI的军事作战方案制定与分析平台 - 增强版</h3>
            <p>集成情报分析、作战规划、地图分析、后勤保障等专业军事智能体</p>
        </div>
        """)
        
        # 系统状态和控制
        with gr.Row():
            with gr.Column(scale=2):
                system_status = gr.Textbox(
                    label="🔧 系统状态",
                    value="系统未初始化 - 请点击初始化按钮",
                    interactive=False,
                    elem_classes=["status-box"]
                )
            with gr.Column(scale=1):
                init_btn = gr.Button("🚀 初始化系统", variant="primary", size="lg")
                reset_btn = gr.Button("🔄 重置系统", variant="secondary")
        
        # 主要功能区域
        with gr.Row():
            # 左侧：任务输入区域
            with gr.Column(scale=2, elem_classes=["input-section"]):
                gr.Markdown("## 📝 军事任务输入")
                
                task_input = gr.Textbox(
                    label="军事任务描述",
                    placeholder="""请详细描述军事任务，建议包括以下要素：

🎯 任务背景和目标
🗺️ 地形情况描述
👥 我方兵力配置
⚔️ 敌方情况分析
📋 特殊要求和约束条件
⏰ 时间限制

示例格式：
任务背景：敌方装甲师正向我方控制的战略要地推进，预计48小时内到达...
地形情况：目标地区为山地地形，有多个制高点，主要通道为两条山谷道路...
我方兵力：一个加强步兵旅，配备反坦克武器、迫击炮和防空武器...
敌方情况：一个机械化师，约8000人，装备主战坦克60辆...
任务目标：制定防御作战方案，阻止敌方推进，保卫战略要地...""",
                    lines=12,
                    max_lines=20
                )
                
                with gr.Row():
                    terrain_image = gr.Image(
                        label="🗺️ 地形图上传（可选）",
                        type="pil",
                        height=250
                    )
                    
                    with gr.Column():
                        gr.Markdown("### 📊 图片要求")
                        gr.Markdown("""
                        - 支持格式：PNG, JPG, JPEG
                        - 建议尺寸：800x600以上
                        - 文件大小：< 10MB
                        - 内容：地形图、卫星图、作战地图等
                        """)
                
                with gr.Row():
                    analyze_btn = gr.Button("🎯 开始分析", variant="primary", size="lg")
                    clear_btn = gr.Button("🗑️ 清空输入", variant="secondary")
                    stop_btn = gr.Button("⏹️ 停止分析", variant="stop")
            
            # 右侧：分析过程和结果
            with gr.Column(scale=3, elem_classes=["output-section"]):
                gr.Markdown("## 📊 实时分析过程")
                
                # 进度指示
                progress_info = gr.Textbox(
                    label="当前状态",
                    value="等待任务输入...",
                    interactive=False
                )
                
                analysis_logs = gr.Textbox(
                    label="分析日志",
                    lines=10,
                    max_lines=15,
                    interactive=False,
                    elem_classes=["log-box"]
                )
                
                gr.Markdown("## 📋 军事作战方案")
                
                result_output = gr.Textbox(
                    label="详细作战部署方案",
                    lines=18,
                    max_lines=25,
                    interactive=False,
                    elem_classes=["result-box"]
                )
        
        # 预设任务示例区域
        with gr.Row():
            gr.Markdown("## 🎯 预设军事任务示例")
            
        with gr.Row():
            example_1 = gr.Button("🏔️ 山地防御作战", variant="secondary")
            example_2 = gr.Button("🏙️ 城市攻坚作战", variant="secondary")
            example_3 = gr.Button("🌊 海岸登陆作战", variant="secondary")
            example_4 = gr.Button("🚁 空降突击作战", variant="secondary")
        
        # 系统信息和帮助
        with gr.Row():
            with gr.Column():
                gr.Markdown("""
                ### 📚 使用说明
                1. **初始化系统**：首次使用需要点击"初始化系统"按钮
                2. **输入任务**：详细描述军事任务或选择预设示例
                3. **上传地图**：可选择上传相关地形图或作战地图
                4. **开始分析**：点击"开始分析"按钮，系统将调用多个专业智能体
                5. **查看结果**：在右侧查看实时分析过程和最终作战方案
                """)
            
            with gr.Column():
                gr.Markdown("""
                ### ⚙️ 系统架构
                - **军事参谋长**：统筹协调，制定整体方案
                - **情报分析专家**：分析敌我态势和威胁评估
                - **作战规划专家**：制定详细战术和作战计划
                - **地图分析专家**：分析地形地貌和地理优势
                - **后勤保障专家**：规划后勤补给和保障方案
                """)
        
        # 事件处理函数
        def initialize_system():
            """初始化系统"""
            status, logs = sync_initialize()
            return status, logs, "系统初始化完成" if "成功" in status else "初始化失败"
        
        def analyze_task(task_desc, terrain_img):
            """分析任务"""
            if not task_desc.strip():
                return "❌ 请输入军事任务描述", "", "输入错误"
            
            result, logs, status = sync_analyze_task(task_desc, terrain_img)
            return logs, result, status
        
        def clear_inputs():
            """清空输入"""
            return "", None, "输入已清空"
        
        def reset_system():
            """重置系统"""
            app.system_initialized = False
            app.military_chief = None
            app.clear_logs()
            return "系统已重置，请重新初始化", "", "系统已重置"
        
        def load_example_1():
            return """任务背景：敌方装甲师正向我方控制的战略要地推进，预计48小时内到达。该要地控制着重要的交通枢纽和补给线，对整个战区具有重要战略意义。

地形情况：目标地区为山地地形，海拔500-1200米，有三个主要制高点，主要通道为两条山谷道路，地形复杂，植被茂密，有一条河流从东向西穿过，河上有两座桥梁。山地坡度较陡，不利于装甲车辆机动。

我方兵力：一个加强步兵旅，约4500人，配备反坦克导弹、迫击炮、防空导弹和工兵装备。另有一个炮兵营提供火力支援。

敌方情况：一个机械化师，约8000人，装备主战坦克60辆，装甲车120辆，自行火炮24门，具备空中支援能力。敌方具有火力和机动优势，但对山地作战经验不足。

任务目标：制定防御作战方案，充分利用地形优势，阻止敌方推进，保卫战略要地至少72小时，等待后续增援。"""
        
        def load_example_2():
            return """任务背景：需要夺取敌方控制的重要城市，该城市是敌方的后勤补给中心和指挥枢纽，控制该城市将切断敌方补给线。

地形情况：目标城市位于平原地区，城区面积约50平方公里，建筑密集，有工业区、居民区和商业区，外围有环城公路，市内道路网发达。城市中心有政府大楼和军事指挥部。

我方兵力：一个合成旅，包括装甲营、机步营、炮兵营和工兵连，约4000人，装备主战坦克40辆，装甲车80辆。另有特种部队一个连配合行动。

敌方情况：一个守备团，约2000人，在城市关键点位构筑了防御工事，有轻型装甲车辆和反坦克武器。敌方在居民区设置了防御阵地，企图利用平民作掩护。

任务目标：制定城市攻坚作战方案，快速夺取城市关键目标，减少平民伤亡，确保城市基础设施完整。"""
        
        def load_example_3():
            return """任务背景：执行两栖登陆作战，夺取敌方控制的沿海重要港口，该港口是敌方海上补给的重要节点。

地形情况：目标海岸线长约5公里，有沙滩和岩石海岸，内陆为丘陵地带，港口设施完整，有多个码头和仓库。海岸防御工事较为完善。

我方兵力：一个海军陆战旅，配备两栖装甲车、登陆艇和直升机支援，约3500人。海军提供火力支援，空军提供空中掩护。

敌方情况：一个海防团，约1500人，在海岸线构筑了防御工事，配备海防炮和反舰导弹。另有快速反应部队可在2小时内到达。

任务目标：制定两栖登陆作战方案，快速夺取港口，建立稳固的滩头阵地，为后续部队登陆创造条件。"""
        
        def load_example_4():
            return """任务背景：执行空降突击作战，夺取敌方后方重要机场，切断敌方空中补给线和撤退路线。

地形情况：目标机场位于平原地区，跑道长3000米，有完整的航站楼和维修设施。机场周围地形开阔，有少量树林和村庄。

我方兵力：一个空降突击营，约800人，配备轻型装甲车、反坦克武器和通信设备。运输机和武装直升机提供支援。

敌方情况：机场守备部队约500人，配备防空武器和轻型装甲车。敌方可在4小时内调集增援部队约2000人。

任务目标：制定空降突击作战方案，快速夺取并控制机场，阻止敌方使用该机场，坚守至主力部队到达。"""
        
        # 绑定事件
        init_btn.click(
            fn=initialize_system,
            outputs=[system_status, analysis_logs, progress_info]
        )
        
        reset_btn.click(
            fn=reset_system,
            outputs=[system_status, analysis_logs, progress_info]
        )
        
        analyze_btn.click(
            fn=analyze_task,
            inputs=[task_input, terrain_image],
            outputs=[analysis_logs, result_output, progress_info]
        )
        
        clear_btn.click(
            fn=clear_inputs,
            outputs=[task_input, terrain_image, progress_info]
        )
        
        example_1.click(fn=load_example_1, outputs=[task_input])
        example_2.click(fn=load_example_2, outputs=[task_input])
        example_3.click(fn=load_example_3, outputs=[task_input])
        example_4.click(fn=load_example_4, outputs=[task_input])
    
    return interface

def main():
    """主函数"""
    print("🚀 启动军事参谋智能体Web系统 (增强版)")
    print("=" * 60)
    
    # 创建增强版Gradio界面
    interface = create_enhanced_gradio_interface()
    
    # 启动Web服务
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True,
        show_error=True,
        inbrowser=True,
        favicon_path=None,
        ssl_verify=False
    )

if __name__ == "__main__":
    main() 