@echo off
echo 启动 PS-MCP 图片处理服务器...

REM 检查 uv 是否已安装
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到 uv 命令
    echo 请先安装 uv: https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

REM 启动服务器
uv run python main.py

pause