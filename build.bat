@echo off
chcp 65001 >nul 2>&1
echo.
echo ══════════════════════════════════════════════
echo   TwoYaTimer 打包脚本
echo ══════════════════════════════════════════════
echo.

:: ── 检查 Python 环境 ──
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

:: ── 安装依赖 ──
echo [1/3] 安装依赖...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

:: ── 获取 customtkinter 路径（PyInstaller 需要包含其资源文件）──
echo [2/3] 定位 customtkinter 资源...
for /f "delims=" %%i in ('python -c "import customtkinter; import os; print(os.path.dirname(customtkinter.__file__))"') do set CTK_PATH=%%i

if "%CTK_PATH%"=="" (
    echo [错误] 无法定位 customtkinter 包
    pause
    exit /b 1
)
echo     customtkinter: %CTK_PATH%

:: ── 执行 PyInstaller 打包 ──
echo [3/3] 开始打包...
echo.

pyinstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name TwoYaTimer ^
    --add-data "%CTK_PATH%;customtkinter/" ^
    --hidden-import customtkinter ^
    --clean ^
    src\main.py

if errorlevel 1 (
    echo.
    echo [错误] 打包失败，请检查上方错误信息
    pause
    exit /b 1
)

echo.
echo ══════════════════════════════════════════════
echo   打包完成！
echo   输出: dist\TwoYaTimer.exe
echo ══════════════════════════════════════════════
echo.

:: ── 显示文件大小 ──
for %%A in (dist\TwoYaTimer.exe) do (
    set /a SIZE_MB=%%~zA / 1048576
    echo   文件大小: %%~zA bytes (~%SIZE_MB% MB^)
)

echo.
pause
