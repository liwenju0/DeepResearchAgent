#!/usr/bin/env python3
"""
军事参谋智能体系统使用示例

这个示例展示了如何使用军事参谋系统来制定作战部署方案。
系统包含：
- 军事参谋长（顶层协调）
- 情报分析专家
- 作战规划专家  
- 地图分析专家
- 后勤保障专家
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import config
from src.models import model_manager
from src.agent import create_agent
from src.logger import logger

async def run_military_scenario():
    """运行军事作战场景"""
    
    # 初始化军事配置
    config.init_config("configs/military_config.toml")
    
    # 初始化日志系统
    logger.init_logger(config.log_path)
    
    # 创建军事参谋系统
    military_chief = create_agent()
    
    # 军事任务场景
    scenarios = [
        {
            "name": "山地防御作战",
            "task": """
            任务背景：敌方装甲师正向我方控制的战略要地推进，预计48小时内到达。
            
            地形情况：目标地区为山地地形，有多个制高点，主要通道为两条山谷道路，
            地形复杂，植被茂密，有一条河流穿过。
            
            我方兵力：一个加强步兵旅，配备反坦克武器、迫击炮和防空武器。
            
            敌方情况：一个机械化师，约8000人，装备主战坦克60辆，装甲车120辆，
            自行火炮24门，具备空中支援能力。
            
            任务目标：制定防御作战方案，阻止敌方推进，保卫战略要地。
            """
        },
        {
            "name": "城市攻坚作战", 
            "task": """
            任务背景：需要夺取敌方控制的重要城市，该城市是敌方的后勤补给中心。
            
            地形情况：目标城市位于平原地区，城区建筑密集，有工业区、居民区和商业区，
            外围有环城公路，市内道路网发达。
            
            我方兵力：一个合成旅，包括装甲营、机步营、炮兵营和工兵连，
            约4000人，装备主战坦克40辆。
            
            敌方情况：一个守备团，约2000人，在城市关键点位构筑了防御工事，
            有轻型装甲车辆和反坦克武器。
            
            任务目标：制定城市攻坚作战方案，快速夺取城市，减少平民伤亡。
            """
        }
    ]
    
    # 运行军事场景
    for scenario in scenarios:
        print(f"\n{'='*60}")
        print(f"🎯 军事场景：{scenario['name']}")
        print(f"{'='*60}")
        
        try:
            # 执行军事任务规划
            result = await military_chief(scenario['task'])
            
            print(f"\n📋 作战部署方案：")
            print(f"{'-'*40}")
            print(result)
            
        except Exception as e:
            logger.error(f"军事场景执行失败: {e}")
            print(f"❌ 场景执行失败: {e}")

async def run_map_analysis_demo():
    """演示地图分析功能"""
    print(f"\n{'='*60}")
    print(f"🗺️  地图分析演示")
    print(f"{'='*60}")
    
    # 初始化配置
    config.init_config("configs/military_config.toml")
    
    # 初始化日志系统
    logger.init_logger(config.log_path)
    
    military_chief = create_agent()
    
    map_analysis_task = """
    请分析以下作战地区的地形特征：
    
    地区描述：该地区为丘陵地带，海拔200-800米，有三个主要高地控制点，
    地区内有一条主要河流从东向西流过，河上有两座桥梁。
    植被以森林和灌木为主，覆盖率约60%。
    有一条主要公路和两条次要道路穿过该地区。
    
    请提供详细的地形分析和军事价值评估。
    """
    
    try:
        result = await military_chief(map_analysis_task)
        print(f"\n📊 地形分析结果：")
        print(f"{'-'*40}")
        print(result)
    except Exception as e:
        logger.error(f"地图分析失败: {e}")
        print(f"❌ 地图分析失败: {e}")

def main():
    """主函数"""
    print("🚀 启动军事参谋智能体系统")
    print("=" * 60)
    model_manager.init_models()
    # 运行军事场景
    asyncio.run(run_military_scenario())
    
    # 运行地图分析演示
    asyncio.run(run_map_analysis_demo())
    
    print(f"\n✅ 军事参谋系统演示完成")

if __name__ == "__main__":
    main() 