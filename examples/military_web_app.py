#!/usr/bin/env python3
"""
军事参谋智能体系统 Web 界面

基于Gradio构建的Web应用，提供：
- 军事任务输入界面
- 地形图上传功能
- 实时分析过程展示
- 军事方案输出
"""

import asyncio
import sys
import os
import gradio as gr
import threading
import time
from datetime import datetime
from typing import Optional, List, Tuple
import base64
from io import BytesIO
from PIL import Image

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import config
from src.models import model_manager
from src.agent import create_agent
from src.logger import logger

class MilitaryWebApp:
    """军事参谋Web应用类"""
    
    def __init__(self):
        self.military_chief = None
        self.analysis_logs = []
        self.current_task_id = None
        
    async def initialize_system(self):
        """初始化军事参谋系统"""
        try:
            # 初始化配置
            config.init_config("configs/military_config.toml")
            
            # 初始化日志系统
            logger.init_logger(config.log_path)
            
            # 初始化模型管理器
            model_manager.init_models()
            
            # 创建军事参谋系统
            self.military_chief = create_agent()
            
            return "✅ 军事参谋系统初始化成功"
        except Exception as e:
            logger.error(f"系统初始化失败: {e}")
            return f"❌ 系统初始化失败: {str(e)}"
    
    def add_analysis_log(self, message: str, log_type: str = "info"):
        """添加分析日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.analysis_logs.append(log_entry)
        return "\n".join(self.analysis_logs)
    
    def clear_logs(self):
        """清空日志"""
        self.analysis_logs = []
        return ""
    
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
    
    async def analyze_military_task(
        self, 
        task_description: str, 
        terrain_image: Optional[Image.Image],
        progress_callback=None
    ) -> Tuple[str, str]:
        """分析军事任务"""
        if not self.military_chief:
            return "❌ 系统未初始化，请先初始化系统", ""
        
        if not task_description.strip():
            return "❌ 请输入军事任务描述", ""
        
        try:
            # 生成任务ID
            self.current_task_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 清空之前的日志
            self.clear_logs()
            
            # 添加初始日志
            logs = self.add_analysis_log("🚀 开始军事任务分析")
            if progress_callback:
                progress_callback(logs)
            
            # 处理地形图
            terrain_info = ""
            if terrain_image:
                terrain_info = self.process_terrain_image(terrain_image)
                logs = self.add_analysis_log(f"🗺️ 地形图处理完成")
                if progress_callback:
                    progress_callback(logs)
            
            # 构建完整的任务描述
            full_task = task_description
            if terrain_info and "✅" in terrain_info:
                full_task += f"\n\n地形图信息：\n{terrain_info}"
            
            # 添加分析开始日志
            logs = self.add_analysis_log("🧠 军事参谋长开始分析任务")
            if progress_callback:
                progress_callback(logs)
            
            # 执行军事任务分析
            result = await self.military_chief(full_task)
            
            # 添加完成日志
            logs = self.add_analysis_log("✅ 军事方案制定完成")
            if progress_callback:
                progress_callback(logs)
            
            return result, logs
            
        except Exception as e:
            error_msg = f"❌ 军事任务分析失败: {str(e)}"
            logger.error(error_msg)
            logs = self.add_analysis_log(error_msg)
            return error_msg, logs

# 创建全局应用实例
app = MilitaryWebApp()

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
            app.analyze_military_task(task_description, terrain_image)
        )
    finally:
        loop.close()

def create_gradio_interface():
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
    }
    
    .log-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        padding: 10px;
        font-family: monospace;
        max-height: 400px;
        overflow-y: auto;
    }
    """
    
    with gr.Blocks(css=custom_css, title="军事参谋智能体系统") as interface:
        
        # 标题和说明
        gr.HTML("""
        <div class="military-header">
            <h1>🎖️ 军事参谋智能体系统</h1>
            <p>基于AI的军事作战方案制定与分析平台</p>
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
            # 左侧：任务输入
            with gr.Column(scale=2):
                gr.Markdown("## 📝 军事任务输入")
                
                task_input = gr.Textbox(
                    label="军事任务描述",
                    placeholder="""请详细描述军事任务，包括：
- 任务背景和目标
- 地形情况
- 我方兵力配置
- 敌方情况
- 特殊要求等

示例：
任务背景：敌方装甲师正向我方控制的战略要地推进...
地形情况：目标地区为山地地形，有多个制高点...
我方兵力：一个加强步兵旅，配备反坦克武器...
敌方情况：一个机械化师，约8000人...
任务目标：制定防御作战方案，阻止敌方推进...""",
                    lines=10,
                    max_lines=15
                )
                
                terrain_image = gr.Image(
                    label="🗺️ 地形图上传（可选）",
                    type="pil",
                    height=200
                )
                
                analyze_btn = gr.Button("🎯 开始分析", variant="primary", size="lg")
                clear_btn = gr.Button("🗑️ 清空输入", variant="secondary")
            
            # 右侧：分析过程和结果
            with gr.Column(scale=3):
                gr.Markdown("## 📊 分析过程")
                
                analysis_logs = gr.Textbox(
                    label="实时分析日志",
                    lines=8,
                    max_lines=12,
                    interactive=False,
                    elem_classes=["log-box"]
                )
                
                gr.Markdown("## 📋 军事方案")
                
                result_output = gr.Textbox(
                    label="作战部署方案",
                    lines=15,
                    max_lines=20,
                    interactive=False
                )
        
        # 预设任务示例
        with gr.Row():
            gr.Markdown("## 🎯 预设任务示例")
            
        with gr.Row():
            example_1 = gr.Button("山地防御作战", variant="secondary")
            example_2 = gr.Button("城市攻坚作战", variant="secondary")
            example_3 = gr.Button("海岸登陆作战", variant="secondary")
        
        # 事件处理函数
        def initialize_system():
            return sync_initialize()
        
        def analyze_task(task_desc, terrain_img):
            if not task_desc.strip():
                return "❌ 请输入军事任务描述", ""
            
            result, logs = sync_analyze_task(task_desc, terrain_img)
            return logs, result
        
        def clear_inputs():
            return "", None
        
        def load_example_1():
            return """任务背景：敌方装甲师正向我方控制的战略要地推进，预计48小时内到达。

地形情况：目标地区为山地地形，有多个制高点，主要通道为两条山谷道路，地形复杂，植被茂密，有一条河流穿过。

我方兵力：一个加强步兵旅，配备反坦克武器、迫击炮和防空武器。

敌方情况：一个机械化师，约8000人，装备主战坦克60辆，装甲车120辆，自行火炮24门，具备空中支援能力。

任务目标：制定防御作战方案，阻止敌方推进，保卫战略要地。"""
        
        def load_example_2():
            return """任务背景：需要夺取敌方控制的重要城市，该城市是敌方的后勤补给中心。

地形情况：目标城市位于平原地区，城区建筑密集，有工业区、居民区和商业区，外围有环城公路，市内道路网发达。

我方兵力：一个合成旅，包括装甲营、机步营、炮兵营和工兵连，约4000人，装备主战坦克40辆。

敌方情况：一个守备团，约2000人，在城市关键点位构筑了防御工事，有轻型装甲车辆和反坦克武器。

任务目标：制定城市攻坚作战方案，快速夺取城市，减少平民伤亡。"""
        
        def load_example_3():
            return """任务背景：执行两栖登陆作战，夺取敌方控制的沿海重要港口。

地形情况：目标海岸线长约5公里，有沙滩和岩石海岸，内陆为丘陵地带，港口设施完整，有多个码头。

我方兵力：一个海军陆战旅，配备两栖装甲车、登陆艇和直升机支援，约3500人。

敌方情况：一个海防团，约1500人，在海岸线构筑了防御工事，配备海防炮和反舰导弹。

任务目标：制定两栖登陆作战方案，快速夺取港口，建立滩头阵地。"""
        
        # 绑定事件
        init_btn.click(
            fn=initialize_system,
            outputs=[system_status]
        )
        
        analyze_btn.click(
            fn=analyze_task,
            inputs=[task_input, terrain_image],
            outputs=[analysis_logs, result_output]
        )
        
        clear_btn.click(
            fn=clear_inputs,
            outputs=[task_input, terrain_image]
        )
        
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
    print("🚀 启动军事参谋智能体Web系统")
    print("=" * 60)
    
    # 创建Gradio界面
    interface = create_gradio_interface()
    
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