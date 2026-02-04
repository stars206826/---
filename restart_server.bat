@echo off
echo ========================================
echo 清理Python缓存并重启服务器
echo ========================================

echo.
echo 1. 清理Python缓存文件...
del /s /q *.pyc 2>nul
rmdir /s /q __pycache__ 2>nul

echo.
echo 2. 启动服务器...
echo.
python enhanced_backend_with_edge_tts.py

pause
