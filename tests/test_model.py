import warnings
warnings.simplefilter("ignore", DeprecationWarning)

import os
import sys
from pathlib import Path
import asyncio
from dotenv import load_dotenv
from typing import Dict, List, Tuple

# 加载环境变量
load_dotenv(verbose=True)

root = str(Path(__file__).resolve().parents[1])
sys.path.append(root)

from src.models import model_manager, ModelManager
from src.models.base import ChatMessage, MessageRole
from src.logger import logger

class ModelTestResult:
    """模型测试结果类"""
    def __init__(self, model_name: str, success: bool, error_type: str = None, error_message: str = None, response_preview: str = None):
        self.model_name = model_name
        self.success = success
        self.error_type = error_type
        self.error_message = error_message
        self.response_preview = response_preview

def classify_error(error_message: str) -> str:
    """分类错误类型"""
    error_lower = error_message.lower()
    
    if "model not found" in error_lower:
        return "模型不存在"
    elif "404" in error_lower or "not found" in error_lower:
        return "API端点错误"
    elif "401" in error_lower or "unauthorized" in error_lower:
        return "认证失败"
    elif "403" in error_lower or "forbidden" in error_lower:
        return "权限不足"
    elif "connection" in error_lower or "timeout" in error_lower:
        return "网络连接问题"
    elif "credentials" in error_lower or "application_default_credentials" in error_lower:
        return "认证文件缺失"
    elif "api key" in error_lower:
        return "API密钥问题"
    elif "rate limit" in error_lower:
        return "请求频率限制"
    else:
        return "未知错误"

async def test_model_call(model_name: str, test_message: str = "你好，请简单介绍一下你自己。") -> ModelTestResult:
    """测试单个模型的调用"""
    try:
        if model_name not in model_manager.registed_models:
            return ModelTestResult(
                model_name=model_name,
                success=False,
                error_type="配置错误",
                error_message="模型未注册"
            )
            
        model = model_manager.registed_models[model_name]
        
        # 创建测试消息 - 使用字典格式而不是ChatMessage对象
        messages = [
            {"role": "user", "content": test_message}
        ]
        
        logger.info(f"正在测试模型: {model_name}")
        
        # 调用模型
        response = await model(messages)
        
        response_preview = response.content[:100] if response.content else 'No content'
        logger.info(f"模型 {model_name} 调用成功")
        logger.info(f"响应内容: {response_preview}...")
        
        return ModelTestResult(
            model_name=model_name,
            success=True,
            response_preview=response_preview
        )
        
    except Exception as e:
        error_message = str(e)
        error_type = classify_error(error_message)
        
        logger.error(f"模型 {model_name} 调用失败: {error_message}")
        
        return ModelTestResult(
            model_name=model_name,
            success=False,
            error_type=error_type,
            error_message=error_message
        )

async def test_all_models() -> Tuple[List[ModelTestResult], Dict[str, int]]:
    """测试所有已注册的模型"""
    logger.info("开始测试所有模型...")
    
    # 初始化模型管理器
    use_local_proxy = os.getenv("USE_LOCAL_PROXY", "false").lower() == "true"
    model_manager.init_models(use_local_proxy=use_local_proxy)
    
    logger.info(f"已注册的模型: {list(model_manager.registed_models.keys())}")
    
    results = []
    error_stats = {}
    
    for model_name in model_manager.registed_models.keys():
        result = await test_model_call(model_name)
        results.append(result)
        
        if not result.success:
            error_type = result.error_type
            error_stats[error_type] = error_stats.get(error_type, 0) + 1
    
    return results, error_stats

def print_test_summary(results: List[ModelTestResult], error_stats: Dict[str, int]):
    """打印测试摘要"""
    total_count = len(results)
    success_count = sum(1 for r in results if r.success)
    failure_count = total_count - success_count
    
    print("\n" + "="*60)
    print("📊 模型测试摘要")
    print("="*60)
    print(f"总计: {total_count} 个模型")
    print(f"成功: {success_count} 个模型 ✅")
    print(f"失败: {failure_count} 个模型 ❌")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    if success_count > 0:
        print("\n🎉 成功的模型:")
        for result in results:
            if result.success:
                print(f"  ✅ {result.model_name}")
                if result.response_preview:
                    print(f"     响应预览: {result.response_preview}...")
    
    if failure_count > 0:
        print("\n❌ 失败的模型:")
        for result in results:
            if not result.success:
                print(f"  ❌ {result.model_name}: {result.error_type}")
        
        print("\n📈 错误类型统计:")
        for error_type, count in error_stats.items():
            print(f"  {error_type}: {count} 个模型")
    
    print("="*60)

def check_env_variables() -> bool:
    """检查必要的环境变量是否已设置"""
    logger.info("检查环境变量配置...")
    
    required_vars = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY", 
        "GOOGLE_API_KEY"
    ]
    
    optional_vars = [
        "OPENAI_API_BASE",
        "ANTHROPIC_API_BASE",
        "GOOGLE_API_BASE",
        "QWEN_API_KEY",
        "QWEN_API_BASE",
        "USE_LOCAL_PROXY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            logger.warning(f"缺少必要的环境变量: {var}")
    
    for var in optional_vars:
        if os.getenv(var):
            logger.info(f"可选环境变量已设置: {var}")
        else:
            logger.info(f"可选环境变量未设置: {var}")
    
    if missing_vars:
        logger.error(f"缺少必要的环境变量: {missing_vars}")
        logger.error("请在 .env 文件中配置这些变量")
        print("\n💡 提示: 请创建 .env 文件并配置以下变量:")
        print("OPENAI_API_KEY=your_openai_key")
        print("ANTHROPIC_API_KEY=your_anthropic_key") 
        print("GOOGLE_API_KEY=your_google_key")
        print("# 可选配置:")
        print("USE_LOCAL_PROXY=false")
        return False
    
    logger.info("环境变量检查通过")
    return True

if __name__ == "__main__":
    print("🚀 DeepResearchAgent 模型测试工具")
    print("="*60)
    
    # 检查环境变量
    if not check_env_variables():
        logger.error("环境变量检查失败，退出测试")
        sys.exit(1)
    
    # 运行模型测试
    results, error_stats = asyncio.run(test_all_models())
    
    # 打印测试摘要
    print_test_summary(results, error_stats)
    
    success_count = sum(1 for r in results if r.success)
    total_count = len(results)
    
    if success_count == total_count:
        logger.info("🎉 所有模型测试通过！")
        sys.exit(0)
    elif success_count > 0:
        logger.info(f"✅ 部分模型测试通过 ({success_count}/{total_count})")
        sys.exit(0)  # 部分成功也算通过
    else:
        logger.error("❌ 所有模型测试失败")
        sys.exit(1) 