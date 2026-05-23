#!/bin/bash
echo "========================================"
echo " AutoReply Pro - Build Script"
echo " WinDev Studio"
echo "========================================"

# Зависимости
pip3 install -r requirements.txt --break-system-packages -q

# Компиляция
pyinstaller \
    --onefile \
    --windowed \
    --name "AutoReplyPro" \
    app.py

echo ""
echo "Готово! Файл: dist/AutoReplyPro"
