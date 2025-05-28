#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
军事地形图图片分析工具使用示例

这个示例展示了如何使用 MilitaryImageMapAnalyzer 工具来分析地形图图片。
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
root_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_dir))

from src.models import model_manager
from src.tools.military_image_map_analyzer import MilitaryImageMapAnalyzer
from src.logger import logger

async def analyze_terrain_map_example():
    """军事地形图分析示例"""
    
    print("🎖️  军事地形图图片分析示例")
    print("=" * 60)
    
    try:
        # 初始化模型管理器
        print("🚀 初始化模型管理器...")
        model_manager.init_models(use_local_proxy=True)
        
        # 创建工具实例
        analyzer = MilitaryImageMapAnalyzer()
        print(f"✅ 工具初始化成功: {analyzer.name}")
        
        # 示例1：综合地形分析
        print("\n" + "="*50)
        print("📍 示例1：综合地形分析（攻击任务）")
        print("="*50)
        
        # 注意：这里需要替换为实际的地形图图片路径
        image_path = "data/terrain_map_sample.png"
        
        if Path(image_path).exists():
            result = await analyzer.forward(
                image_path=image_path,
                analysis_focus="comprehensive",
                mission_context="offensive",
                scale_reference="1:50000"
            )
            
            print("📊 分析结果:")
            print(f"🏔️  地形分类: {result.terrain_classification}")
            print(f"📈 高程特征: {result.elevation_features}")
            print(f"🎯 关键地标: {', '.join(result.key_landmarks) if result.key_landmarks else '无'}")
            print(f"🌿 植被分析: {result.vegetation_analysis}")
            print(f"💧 水系特征: {', '.join(result.water_features) if result.water_features else '无'}")
            print(f"🏗️  基础设施: {', '.join(result.infrastructure) if result.infrastructure else '无'}")
            print(f"⚔️  军事评估: {result.military_assessment}")
            print(f"🎯 战术建议: {', '.join(result.tactical_recommendations) if result.tactical_recommendations else '无'}")
            print(f"👁️  可见性分析: {result.visibility_analysis}")
            print(f"🛣️  机动走廊: {', '.join(result.movement_corridors) if result.movement_corridors else '无'}")
        else:
            print(f"⚠️  示例图片不存在: {image_path}")
            print("请将地形图图片放置在指定路径，或修改 image_path 变量")
        
        # 示例2：防御任务战术分析
        print("\n" + "="*50)
        print("📍 示例2：防御任务战术分析")
        print("="*50)
        
        if Path(image_path).exists():
            result2 = await analyzer.forward(
                image_path=image_path,
                analysis_focus="tactical",
                mission_context="defensive",
                scale_reference="1:25000"
            )
            
            print("🛡️  防御分析结果:")
            print(f"⚔️  军事评估: {result2.military_assessment}")
            print(f"🎯 战术建议: {', '.join(result2.tactical_recommendations) if result2.tactical_recommendations else '无'}")
            print(f"👁️  可见性分析: {result2.visibility_analysis}")
        
        # 示例3：后勤任务基础设施分析
        print("\n" + "="*50)
        print("📍 示例3：后勤任务基础设施分析")
        print("="*50)
        
        if Path(image_path).exists():
            result3 = await analyzer.forward(
                image_path=image_path,
                analysis_focus="infrastructure",
                mission_context="logistics"
            )
            
            print("🚛 后勤分析结果:")
            print(f"🏗️  基础设施: {', '.join(result3.infrastructure) if result3.infrastructure else '无'}")
            print(f"🛣️  机动走廊: {', '.join(result3.movement_corridors) if result3.movement_corridors else '无'}")
            print(f"🎯 战术建议: {', '.join(result3.tactical_recommendations) if result3.tactical_recommendations else '无'}")
        
        # 示例4：侦察任务地形分析
        print("\n" + "="*50)
        print("📍 示例4：侦察任务地形分析")
        print("="*50)
        
        if Path(image_path).exists():
            result4 = await analyzer.forward(
                image_path=image_path,
                analysis_focus="terrain",
                mission_context="reconnaissance"
            )
            
            print("🔍 侦察分析结果:")
            print(f"🏔️  地形分类: {result4.terrain_classification}")
            print(f"🎯 关键地标: {', '.join(result4.key_landmarks) if result4.key_landmarks else '无'}")
            print(f"👁️  可见性分析: {result4.visibility_analysis}")
            print(f"🎯 战术建议: {', '.join(result4.tactical_recommendations) if result4.tactical_recommendations else '无'}")
        
    except Exception as e:
        logger.error(f"示例执行失败: {str(e)}")
        print(f"❌ 示例执行失败: {str(e)}")

def print_usage_guide():
    """打印使用指南"""
    print("📖 使用指南")
    print("=" * 40)
    print("1. 准备地形图图片文件（支持 PNG, JPG, JPEG 格式）")
    print("2. 调用 analyzer.forward() 方法进行分析")
    print("3. 根据任务需求选择合适的分析重点和任务背景")
    print("\n🔧 参数说明:")
    print("• image_path: 地形图图片文件路径（必需）")
    print("• analysis_focus: 分析重点")
    print("  - terrain: 地形分析")
    print("  - tactical: 战术分析")
    print("  - infrastructure: 基础设施分析")
    print("  - comprehensive: 综合分析（默认）")
    print("• mission_context: 任务背景")
    print("  - offensive: 攻击任务（默认）")
    print("  - defensive: 防御任务")
    print("  - reconnaissance: 侦察任务")
    print("  - logistics: 后勤任务")
    print("• scale_reference: 地图比例尺参考（可选）")
    
    print("\n💡 使用建议:")
    print("• 使用高分辨率的地形图图片以获得更好的分析效果")
    print("• 根据具体任务选择合适的分析重点和任务背景")
    print("• 提供地图比例尺信息有助于更准确的分析")
    print("• 分析结果可用于军事规划和决策支持")

if __name__ == "__main__":
    print_usage_guide()
    print("\n" + "="*60)
    
    # 运行示例
    asyncio.run(analyze_terrain_map_example())
    
    print("\n✨ 示例完成！")
    print("\n📝 注意事项:")
    print("• 本工具仅用于教育和研究目的")
    print("• 实际军事应用需要专业人员验证")
    print("• 分析结果应结合实地勘察进行确认") 