@echo off
chcp 65001 >nul
echo ========================================
echo 视频UI测试脚本
echo ========================================
echo.
echo 正在启动服务器...
echo 请在浏览器中访问: http://localhost:8000
echo 然后点击"视频生成"标签页测试视频功能
echo.
echo 按 Ctrl+C 停止服务器
echo ========================================
echo.

python enhanced_backend_with_edge_tts.py
