#!/usr/bin/env python3
"""
地图分析智能体图片分析功能测试示例

此示例展示如何使用地图分析智能体分析地形图图片
"""

import warnings
warnings.simplefilter("ignore", DeprecationWarning)

import sys
import asyncio
from pathlib import Path

# 添加项目根目录到路径
root = str(Path(__file__).resolve().parents[1])
sys.path.append(root)

from src.logger import logger
from src.config import config
from src.models import model_manager
# 确保导入工具和智能体模块以触发注册
import src.tools
import src.agent
from src.registry import REGISTED_AGENTS, REGISTED_TOOLS
from src.utils import assemble_project_path

async def test_map_analysis_with_image():
    """测试地图分析智能体的图片分析功能"""
    
    # 初始化配置和日志
    config.init_config(config_path=assemble_project_path("configs/military_config.toml"))
    logger.init_logger(config.log_path)
    logger.info("初始化地图分析智能体图片分析测试")
    
    # 初始化模型
    model_manager.init_models(use_local_proxy=config.use_local_proxy)
    logger.info(f"已注册模型: {', '.join(model_manager.registed_models.keys())}")
    
    # 获取地图分析智能体配置
    map_agent_config = getattr(config.agent, "map_analysis_agent_config")
    
    # 打印已注册的工具用于调试
    logger.info(f"已注册的工具: {list(REGISTED_TOOLS.keys())}")
    
    # 创建工具实例
    tools = []
    for tool_id in map_agent_config.tools:
        if tool_id not in REGISTED_TOOLS:
            raise ValueError(f"工具 ID '{tool_id}' 未注册")
        tools.append(REGISTED_TOOLS[tool_id]())
        logger.info(f"已加载工具: {tool_id}")
    
    # 创建地图分析智能体
    if "map_analysis_agent" not in REGISTED_AGENTS:
        raise ValueError("地图分析智能体未注册")
    
    map_agent = REGISTED_AGENTS["map_analysis_agent"](
        config=map_agent_config,
        model=model_manager.registed_models[map_agent_config.model_id],
        tools=tools,
        max_steps=map_agent_config.max_steps,
        name=map_agent_config.name,
        description=map_agent_config.description,
        provide_run_summary=True,
    )
    
    logger.info("地图分析智能体创建成功")
    
    # 测试任务：分析地形图图片
    task = """
    请分析一张地形图图片，执行以下任务：
    
    1. 使用 military_image_map_analyzer 工具分析图片路径为 'data/test_map.png' 的地形图
    2. 分析重点设置为 'comprehensive'（综合分析）
    3. 任务背景设置为 'offensive'（攻击任务）
    4. 提供详细的地形分析报告，包括：
       - 地形分类和特征
       - 关键地标识别
       - 军事价值评估
       - 战术建议
       - 机动路线规划
    
    请提供完整的地形分析结果。
    """
    
    logger.info("开始执行地形图图片分析任务")
    
    try:
        # 运行分析任务
        result = await map_agent.run(task)
        
        logger.info("=" * 60)
        logger.info("地形图图片分析结果:")
        logger.info("=" * 60)
        logger.info(f"{result}")
        logger.info("=" * 60)
        
        return result
        
    except Exception as e:
        logger.error(f"地形图图片分析失败: {str(e)}")
        raise

async def main():
    """主函数"""
    try:
        result = await test_map_analysis_with_image()
        print("\n✅ 地图分析智能体图片分析功能测试完成")
        print(f"分析结果: {result}")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 