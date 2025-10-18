@echo off
chcp 65001 >nul
title AI创意工坊 - Windows启动器

echo ========================================
echo    AI创意工坊 - Windows启动器
echo ========================================
echo.

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 未找到Python，请先安装Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python环境正常

echo 检查依赖安装...
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 安装依赖包...
pip install -r requirements.txt

echo.
echo 启动AI创意工坊...
echo 应用启动后，请打开浏览器访问: http://localhost:5000
echo 按 Ctrl+C 停止服务
echo.

python app.py

pause