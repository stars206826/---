@echo off
chcp 65001 >nul
REM 会说话的文物 - Windows 快速启动脚本

echo ========================================
echo   会说话的文物 - 快速启动向导
echo ========================================
echo.

REM 检查 Python 版本
echo 🔍 检查 Python 环境...
python --version
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)
echo.

REM 检查依赖
echo 📦 检查依赖包...
python -c "import requests" 2>nul
if errorlevel 1 (
    echo ❌ 缺少必需依赖
    echo.
    choice /C YN /M "是否现在安装依赖"
    if errorlevel 2 (
        echo ⚠️  请手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo 📥 安装依赖中...
    pip install -r requirements.txt
)

echo ✅ 依赖检查完成
echo.

REM 检查配置文件
if not exist ".env" (
    echo ⚠️  未找到 .env 配置文件
    if exist ".env.example" (
        choice /C YN /M "是否从 .env.example 创建配置文件"
        if not errorlevel 2 (
            copy .env.example .env >nul
            echo ✅ 已创建 .env 文件，请编辑填入你的 API 密钥
            echo    主要配置项：
            echo    - SILICONFLOW_KEY: https://siliconflow.cn 注册获取
            echo.
            pause
        )
    )
)

echo.
echo 🚀 启动服务器...
echo    访问地址: http://localhost:8000
echo    按 Ctrl+C 停止服务
echo.
echo ========================================
echo.

REM 启动主服务器
python enhanced_backend_with_edge_tts.py
