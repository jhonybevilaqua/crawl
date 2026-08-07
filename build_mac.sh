#!/bin/bash
cd "$(dirname "$0")"

echo "=========================================="
echo "  BUILD - CRAWL TV EVANGELIZAR (macOS)"
echo "=========================================="
echo ""

if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python 3 nao encontrado."
    exit 1
fi

pip3 install pyinstaller

echo "Compilando app bundle..."

python3 -m PyInstaller     --name="CRAWL TV EVANGELIZAR"     --windowed     --onefile     --add-data="config.json:."     --add-data="quotes_history.json:."     --add-data="index.html:."     --clean     --noconfirm     app.py

if [ $? -eq 0 ]; then
    echo ""
    echo "SUCESSO!"
    echo "App: dist/CRAWL TV EVANGELIZAR"
else
    echo "ERRO na compilacao."
fi
