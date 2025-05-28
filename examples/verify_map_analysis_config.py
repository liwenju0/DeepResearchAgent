#!/usr/bin/env python3
"""
验证地图分析智能体配置脚本

此脚本验证地图分析智能体是否正确配置了军事地形图图片分析工具
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
root = str(Path(__file__).resolve().parents[1])
sys.path.append(root)

def verify_tool_registration():
    """验证工具注册"""
    print("🔍 验证工具注册...")
    
    # 导入工具模块以触发注册
    import src.tools
    from src.registry import REGISTED_TOOLS
    
    required_tools = ["military_map_analyzer", "military_image_map_analyzer"]
    
    print(f"已注册的工具: {list(REGISTED_TOOLS.keys())}")
    
    for tool in required_tools:
        if tool in REGISTED_TOOLS:
            print(f"✅ 工具 '{tool}' 已正确注册")
        else:
            print(f"❌ 工具 '{tool}' 未注册")
            return False
    
    return True

def verify_agent_registration():
    """验证智能体注册"""
    print("\n🔍 验证智能体注册...")
    
    # 导入智能体模块以触发注册
    import src.agent
    from src.registry import REGISTED_AGENTS
    
    if "map_analysis_agent" in REGISTED_AGENTS:
        print("✅ 地图分析智能体已正确注册")
        return True
    else:
        print("❌ 地图分析智能体未注册")
        return False

def verify_config():
    """验证配置文件"""
    print("\n🔍 验证配置文件...")
    
    from src.config import config
    from src.utils import assemble_project_path
    
    try:
        config.init_config(config_path=assemble_project_path("configs/military_config.toml"))
        
        # 检查地图分析智能体配置
        map_agent_config = getattr(config.agent, "map_analysis_agent_config", None)
        
        if map_agent_config is None:
            print("❌ 地图分析智能体配置未找到")
            return False
        
        print(f"✅ 地图分析智能体配置已找到")
        print(f"   - 名称: {map_agent_config.name}")
        print(f"   - 描述: {map_agent_config.description}")
        print(f"   - 最大步数: {map_agent_config.max_steps}")
        print(f"   - 工具列表: {map_agent_config.tools}")
        
        # 检查是否包含必需的工具
        required_tools = ["military_image_map_analyzer"]
        for tool in required_tools:
            if tool in map_agent_config.tools:
                print(f"✅ 配置包含工具 '{tool}'")
            else:
                print(f"❌ 配置缺少工具 '{tool}'")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 配置验证失败: {str(e)}")
        return False

def verify_agent_creation():
    """验证智能体创建"""
    print("\n🔍 验证智能体创建...")
    
    try:
        from src.config import config
        from src.models import model_manager
        from src.registry import REGISTED_AGENTS, REGISTED_TOOLS
        from src.utils import assemble_project_path
        
        # 初始化配置
        config.init_config(config_path=assemble_project_path("configs/military_config.toml"))
        
        # 初始化模型（使用本地代理设置）
        model_manager.init_models(use_local_proxy=config.use_local_proxy)
        
        # 获取配置
        map_agent_config = getattr(config.agent, "map_analysis_agent_config")
        
        # 创建工具实例
        tools = []
        for tool_id in map_agent_config.tools:
            if tool_id not in REGISTED_TOOLS:
                print(f"❌ 工具 '{tool_id}' 未注册")
                return False
            tools.append(REGISTED_TOOLS[tool_id]())
            print(f"✅ 工具 '{tool_id}' 创建成功")
        
        # 创建智能体
        map_agent = REGISTED_AGENTS["map_analysis_agent"](
            config=map_agent_config,
            model=model_manager.registed_models[map_agent_config.model_id],
            tools=tools,
            max_steps=map_agent_config.max_steps,
            name=map_agent_config.name,
            description=map_agent_config.description,
            provide_run_summary=True,
        )
        
        print("✅ 地图分析智能体创建成功")
        print(f"   - 智能体名称: {map_agent.name}")
        print(f"   - 可用工具数量: {len(map_agent.tools)}")
        print(f"   - 工具列表: {list(map_agent.tools.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ 智能体创建失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 开始验证地图分析智能体配置...")
    print("=" * 60)
    
    # 执行各项验证
    checks = [
        ("工具注册", verify_tool_registration),
        ("智能体注册", verify_agent_registration),
        ("配置文件", verify_config),
        ("智能体创建", verify_agent_creation),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name}验证时发生异常: {str(e)}")
            results.append((check_name, False))
    
    # 输出总结
    print("\n" + "=" * 60)
    print("📊 验证结果总结:")
    print("=" * 60)
    
    all_passed = True
    for check_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{check_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("🎉 所有验证通过！地图分析智能体已正确配置军事地形图图片分析工具。")
        print("\n📝 使用说明:")
        print("- 可以使用 military_image_map_analyzer 工具分析地形图图片")
        print("- 运行测试示例: python examples/test_map_analysis_with_image.py")
        print("- 查看文档: docs/map_analysis_agent_image_support.md")
    else:
        print("⚠️  部分验证失败，请检查配置。")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 