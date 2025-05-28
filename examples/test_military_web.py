#!/usr/bin/env python3
"""
军事参谋Web应用测试脚本

用于验证Web应用的基本功能是否正常
"""

import sys
import os
import asyncio
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """测试导入依赖"""
    print("🔍 测试导入依赖...")
    
    try:
        import gradio as gr
        print("✅ Gradio 导入成功")
    except ImportError as e:
        print(f"❌ Gradio 导入失败: {e}")
        return False
    
    try:
        from src.config import config
        from src.models import model_manager
        from src.agent import create_agent
        from src.logger import logger
        print("✅ 项目模块导入成功")
    except ImportError as e:
        print(f"❌ 项目模块导入失败: {e}")
        return False
    
    return True

def test_config():
    """测试配置文件"""
    print("\n🔍 测试配置文件...")
    
    config_path = "../configs/military_config.toml"
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        return False
    
    try:
        from src.config import config
        config.init_config(config_path)
        print("✅ 配置文件加载成功")
        return True
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return False

def test_env_file():
    """测试环境变量文件"""
    print("\n🔍 测试环境变量...")
    
    env_path = "../.env"
    if not os.path.exists(env_path):
        print(f"⚠️ .env 文件不存在，请创建并配置API密钥")
        return False
    
    # 检查关键环境变量
    try:
        # 尝试导入python-dotenv
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
        except ImportError:
            print("⚠️ python-dotenv 未安装，跳过环境变量检查")
            return True
        
        api_keys = [
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY", 
            "GOOGLE_API_KEY"
        ]
        
        found_keys = []
        for key in api_keys:
            if os.getenv(key):
                found_keys.append(key)
        
        if found_keys:
            print(f"✅ 找到API密钥: {', '.join(found_keys)}")
            return True
        else:
            print("⚠️ 未找到API密钥，请配置至少一个")
            return False
            
    except Exception as e:
        print(f"❌ 环境变量加载失败: {e}")
        return False

async def test_agent_creation():
    """测试智能体创建"""
    print("\n🔍 测试智能体创建...")
    
    try:
        from src.config import config
        from src.models import model_manager
        from src.agent import create_agent
        from src.logger import logger
        
        # 初始化配置
        config.init_config("../configs/military_config.toml")
        
        # 初始化日志
        logger.init_logger(config.log_path)
        
        # 初始化模型
        model_manager.init_models()
        
        # 创建智能体
        agent = create_agent()
        
        print("✅ 军事参谋智能体创建成功")
        return True
        
    except Exception as e:
        print(f"❌ 智能体创建失败: {e}")
        return False

def test_gradio_interface():
    """测试Gradio界面创建"""
    print("\n🔍 测试Gradio界面...")
    
    try:
        import gradio as gr
        
        # 创建简单测试界面
        with gr.Blocks() as demo:
            gr.Markdown("# 测试界面")
            input_text = gr.Textbox(label="输入")
            output_text = gr.Textbox(label="输出")
            
            def test_function(text):
                return f"收到: {text}"
            
            input_text.change(fn=test_function, inputs=input_text, outputs=output_text)
        
        print("✅ Gradio界面创建成功")
        return True
        
    except Exception as e:
        print(f"❌ Gradio界面创建失败: {e}")
        return False

def test_directory_structure():
    """测试目录结构"""
    print("\n🔍 测试目录结构...")
    
    required_dirs = [
        "../src",
        "../src/agent", 
        "../src/config",
        "../src/models",
        "../configs",
        "."  # examples目录
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ 缺少目录: {', '.join(missing_dirs)}")
        return False
    else:
        print("✅ 目录结构完整")
        return True

def create_sample_env():
    """创建示例环境变量文件"""
    print("\n🔧 创建示例.env文件...")
    
    sample_env = """# 军事参谋智能体系统环境变量配置

# 基础设置
PYTHONWARNINGS=ignore
ANONYMIZED_TELEMETRY=false

# OpenAI API配置
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API配置  
ANTHROPIC_API_BASE=https://api.anthropic.com
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google API配置
GOOGLE_API_BASE=https://generativelanguage.googleapis.com
GOOGLE_API_KEY=your_google_api_key_here

# 其他配置
HUGGINGFACE_API_KEY=your_huggingface_key_here
"""
    
    try:
        with open("../.env.example", "w", encoding="utf-8") as f:
            f.write(sample_env)
        print("✅ 创建 .env.example 文件成功")
        print("请复制为 .env 并配置实际的API密钥")
        return True
    except Exception as e:
        print(f"❌ 创建示例文件失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🎖️ 军事参谋Web应用测试")
    print("=" * 50)
    
    # 记录测试结果
    test_results = []
    
    # 运行测试
    test_results.append(("导入依赖", test_imports()))
    test_results.append(("目录结构", test_directory_structure()))
    test_results.append(("配置文件", test_config()))
    test_results.append(("环境变量", test_env_file()))
    test_results.append(("Gradio界面", test_gradio_interface()))
    
    # 异步测试
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        agent_test = loop.run_until_complete(test_agent_creation())
        test_results.append(("智能体创建", agent_test))
        loop.close()
    except Exception as e:
        print(f"❌ 异步测试失败: {e}")
        test_results.append(("智能体创建", False))
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:12} : {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！可以启动Web应用")
        print("\n启动命令:")
        print("python military_web_simple.py")
    else:
        print("⚠️ 部分测试失败，请检查配置")
        
        # 如果环境变量文件不存在，创建示例
        if not os.path.exists("../.env"):
            create_sample_env()
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main() 