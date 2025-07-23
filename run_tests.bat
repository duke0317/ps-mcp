@echo off
echo Running PS-MCP Image Processing Tests...
echo.

REM Check if uv is installed
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: uv command not found
    echo Please install uv: https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

REM Check if test image exists
if not exist "tests\test_image.png" (
    echo Error: Test image not found - tests\test_image.png
    echo Please ensure test image exists
    pause
    exit /b 1
)

echo Using test image: tests\test_image.png
echo Starting tests with uv virtual environment...
echo.

REM Run tests
uv run python tests\test_call_mcp.py

echo.
echo Tests completed!
pause