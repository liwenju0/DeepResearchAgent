#!/usr/bin/env python3
"""
军事参谋智能体系统 Web 界面 (简化版)

简化版特点：
- 更简洁的界面设计
- 更快的启动速度
- 更少的依赖要求
- 更稳定的运行
"""

import asyncio
import sys
import os
import gradio as gr
from datetime import datetime
from typing import Optional
from PIL import Image

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import config
from src.models import model_manager
from src.agent import create_agent
from src.logger import logger

class SimpleMilitaryApp:
    """简化版军事参谋应用"""
    
    def __init__(self):
        self.military_chief = None
        self.initialized = False
        
    def initialize(self):
        """初始化系统"""
        try:
            if self.initialized:
                return "✅ 系统已初始化"
            
            # 初始化配置
            config.init_config("configs/military_config.toml")
            
            # 初始化日志
            logger.init_logger(config.log_path)
            
            # 初始化模型
            model_manager.init_models()
            
            # 创建智能体
            self.military_chief = create_agent()
            
            self.initialized = True
            return "✅ 军事参谋系统初始化成功！"
            
        except Exception as e:
            return f"❌ 初始化失败: {str(e)}"
    
    async def analyze_task(self, task_description: str, terrain_image: Optional[Image.Image] = None):
        """分析军事任务"""
        if not self.initialized:
            return "❌ 请先初始化系统"
        
        if not task_description.strip():
            return "❌ 请输入任务描述"
        
        try:
            # 处理地形图
            full_task = task_description
            if terrain_image:
                # 保存图片
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                os.makedirs("workdir", exist_ok=True)
                image_path = f"workdir/terrain_{timestamp}.png"
                terrain_image.save(image_path)
                full_task += f"\n\n[已上传地形图: {image_path}]"
            
            # 执行分析
            result = await self.military_chief(full_task)
            return result
            
        except Exception as e:
            return f"❌ 分析失败: {str(e)}"

# 创建应用实例
app = SimpleMilitaryApp()

def sync_initialize():
    """同步初始化"""
    return app.initialize()

def sync_analyze(task_desc, terrain_img):
    """同步分析"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(app.analyze_task(task_desc, terrain_img))
    finally:
        loop.close()

def create_simple_interface():
    """创建简化界面"""
    
    with gr.Blocks(title="军事参谋智能体系统") as interface:
        
        # 标题
        gr.HTML("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #1e3c72, #2a5298); color: white; border-radius: 10px; margin-bottom: 20px;">
            <h1>🎖️ 军事参谋智能体系统</h1>
            <p>基于AI的军事作战方案制定平台</p>
        </div>
        """)
        
        # 系统控制
        with gr.Row():
            init_btn = gr.Button("🚀 初始化系统", variant="primary")
            status_text = gr.Textbox(label="系统状态", value="未初始化", interactive=False)
        
        # 主要功能
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 📝 任务输入")
                
                task_input = gr.Textbox(
                    label="军事任务描述",
                    placeholder="""请描述军事任务，例如：

任务背景：敌方部队向我方阵地推进...
地形情况：山地地形，有制高点...
我方兵力：步兵旅，配备反坦克武器...
敌方情况：机械化师，装备坦克...
任务目标：制定防御方案...""",
                    lines=8
                )
                
                terrain_image = gr.Image(
                    label="🗺️ 地形图（可选）",
                    type="pil",
                    height=200
                )
                
                analyze_btn = gr.Button("🎯 开始分析", variant="primary", size="lg")
            
            with gr.Column():
                gr.Markdown("## 📋 分析结果")
                
                result_output = gr.Textbox(
                    label="军事方案",
                    lines=20,
                    interactive=False
                )
        
        # 示例按钮
        gr.Markdown("## 🎯 快速示例")
        with gr.Row():
            example1_btn = gr.Button("山地防御", variant="secondary")
            example2_btn = gr.Button("城市攻坚", variant="secondary")
            example3_btn = gr.Button("登陆作战", variant="secondary")
        
        # 事件绑定
        init_btn.click(
            fn=sync_initialize,
            outputs=[status_text]
        )
        
        analyze_btn.click(
            fn=sync_analyze,
            inputs=[task_input, terrain_image],
            outputs=[result_output]
        )
        
        def load_example1():
            return """任务背景：敌方装甲师向我方战略要地推进，预计48小时到达。

地形情况：山地地形，有三个制高点，两条山谷道路，地形复杂。

我方兵力：加强步兵旅，配备反坦克武器、迫击炮。

敌方情况：机械化师8000人，主战坦克60辆，装甲车120辆。

任务目标：制定防御方案，阻止敌方推进。"""
        
        def load_example2():
            return """任务背景：夺取敌方控制的重要城市，切断补给线。

地形情况：平原城市，建筑密集，道路网发达。

我方兵力：合成旅4000人，主战坦克40辆。

敌方情况：守备团2000人，构筑防御工事。

任务目标：快速夺取城市，减少伤亡。"""
        
        def load_example3():
            return """任务背景：两栖登陆夺取沿海港口。

地形情况：海岸线5公里，有沙滩和岩石海岸。

我方兵力：海军陆战旅3500人，两栖装甲车。

敌方情况：海防团1500人，海岸防御工事。

任务目标：建立滩头阵地，夺取港口。"""
        
        example1_btn.click(fn=load_example1, outputs=[task_input])
        example2_btn.click(fn=load_example2, outputs=[task_input])
        example3_btn.click(fn=load_example3, outputs=[task_input])
    
    return interface

def main():
    """主函数"""
    print("🚀 启动军事参谋智能体Web系统 (简化版)")
    print("=" * 50)
    
    interface = create_simple_interface()
    
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )

if __name__ == "__main__":
    main() 