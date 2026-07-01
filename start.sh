#!/bin/bash
# 会说话的文物 - 快速启动脚本

echo "========================================"
echo "  会说话的文物 - 快速启动向导"
echo "========================================"
echo ""

# 检查 Python 版本
echo "🔍 检查 Python 环境..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✅ Python 版本: $python_version"
echo ""

# 检查依赖
echo "📦 检查依赖包..."
missing_deps=()

if ! python -c "import requests" 2>/dev/null; then
    missing_deps+=("requests")
fi

if ! python -c "import neo4j" 2>/dev/null; then
    echo "⚠️  Neo4j 未安装（可选，但推荐安装以启用知识图谱功能）"
fi

if ! python -c "import edge_tts" 2>/dev/null; then
    echo "⚠️  Edge TTS 未安装（可选，但推荐安装以启用自然语音）"
fi

if ! python -c "from dotenv import load_dotenv" 2>/dev/null; then
    missing_deps+=("python-dotenv")
fi

if [ ${#missing_deps[@]} -gt 0 ]; then
    echo ""
    echo "❌ 缺少必需依赖: ${missing_deps[*]}"
    echo ""
    read -p "是否现在安装缺少的依赖？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📥 安装依赖中..."
        pip install -r requirements.txt
    else
        echo "⚠️  请手动运行: pip install -r requirements.txt"
        exit 1
    fi
fi

echo "✅ 依赖检查完成"
echo ""

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 配置文件"
    if [ -f ".env.example" ]; then
        read -p "是否从 .env.example 创建配置文件？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cp .env.example .env
            echo "✅ 已创建 .env 文件，请编辑填入你的 API 密钥"
            echo "   主要配置项："
            echo "   - SILICONFLOW_KEY: https://siliconflow.cn 注册获取"
            echo ""
            read -p "按回车键继续..."
        fi
    fi
fi

echo ""
echo "🚀 启动服务器..."
echo "   访问地址: http://localhost:8000"
echo "   按 Ctrl+C 停止服务"
echo ""
echo "========================================"
echo ""

# 启动主服务器
python enhanced_backend_with_edge_tts.py
