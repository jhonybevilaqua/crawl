#!/bin/bash
cd "$(dirname "$0")"

echo "=========================================="
echo "  CRAWL TV EVANGELIZAR"
echo "=========================================="
echo ""

if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python 3 nao encontrado."
    echo "Instale com: brew install python3"
    exit 1
fi

echo "Python: $(python3 --version)"
echo ""

echo "[1/2] Instalando dependencias..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERRO ao instalar dependencias."
    exit 1
fi

echo ""
echo "[2/2] Iniciando servidor..."
echo ""
echo "Acesse localmente:  http://localhost:5000"
echo "Acesse na rede:     http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "Pressione CTRL+C para encerrar"
echo ""

python3 app.py
