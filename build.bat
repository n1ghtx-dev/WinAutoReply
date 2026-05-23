@echo off
echo ========================================
echo  AutoReply Pro - Build Script
echo  WinDev Studio
echo ========================================
echo.

:: Проверяем Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python не найден!
    echo Скачай: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Устанавливаем зависимости...
pip install -r requirements.txt -q

echo [2/3] Компилируем в .exe...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "AutoReplyPro" ^
    --icon=icon.ico ^
    --add-data "config.json;." ^
    app.py

echo [3/3] Готово!
echo.
echo Файл: dist\AutoReplyPro.exe
echo.
pause
