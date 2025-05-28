#!/bin/bash

# 军事参谋智能体Web系统启动脚本

echo "🎖️ 军事参谋智能体Web系统启动脚本"
echo "=" * 60

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "../.venv" ]; then
    echo "⚠️ 虚拟环境不存在，正在创建..."
    cd ..
    python3 -m venv .venv
    cd examples
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source ../.venv/bin/activate

# 检查并安装依赖
echo "📦 检查依赖包..."
if ! python -c "import gradio" &> /dev/null; then
    echo "📥 安装Gradio..."
    pip install gradio>=5.0.0
fi

# 检查配置文件
if [ ! -f "../configs/military_config.toml" ]; then
    echo "❌ 军事配置文件不存在: configs/military_config.toml"
    echo "请确保配置文件存在"
    exit 1
fi

# 检查环境变量文件
if [ ! -f "../.env" ]; then
    echo "⚠️ .env 文件不存在，请创建并配置API密钥"
    echo "参考 .env.example 文件"
fi

# 创建工作目录
mkdir -p ../workdir

echo "🚀 启动军事参谋Web系统..."
echo "📱 Web界面将在浏览器中自动打开"
echo "🌐 访问地址: http://localhost:7860"
echo "⏹️ 按 Ctrl+C 停止服务"
echo ""

# 启动Web应用
python military_web_app_enhanced.py 