@echo off
echo ========================================
echo 清理并重启服务器
echo ========================================

echo.
echo [1/5] 停止现有服务器进程...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo [2/5] 清理Python缓存...
del /s /q *.pyc 2>nul
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

echo.
echo [3/5] 验证端口8000已释放...
netstat -ano | findstr :8000
if %errorlevel% equ 0 (
    echo ⚠️ 端口8000仍被占用，请手动关闭
    pause
    exit /b 1
)

echo.
echo [4/5] 启动服务器...
start "会说话的文物服务器" python enhanced_backend_with_edge_tts.py

echo.
echo [5/5] 等待服务器启动...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo 测试服务器端点
echo ========================================
python test_endpoints.py

echo.
echo ========================================
echo 完成！
echo ========================================
pause
