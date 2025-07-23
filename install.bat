@echo off
echo 安装 PS-MCP 图片处理服务器...
echo.

REM 检查是否安装了 uv
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未找到 uv 命令。请先安装 uv:
    echo powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    pause
    exit /b 1
)

echo 正在安装依赖...
uv sync

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 安装完成！
    echo.
    echo 使用方法:
    echo   运行服务器: run.bat
    echo   或者: uv run ps-mcp
    echo.
) else (
    echo.
    echo ❌ 安装失败，请检查错误信息
)

pause