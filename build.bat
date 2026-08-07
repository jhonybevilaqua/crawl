@echo off
chcp 65001 >nul
title Build - CRAWL TV EVANGELIZAR

cd /d "%~dp0"

echo ==========================================
echo   BUILD - CRAWL TV EVANGELIZAR
echo ==========================================
echo.

if not exist "requirements.txt" (
    echo ERRO: requirements.txt nao encontrado.
    pause
    exit /b 1
)

python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado.
    pause
    exit /b 1
)

echo [1/4] Python detectado:
python --version
echo.

echo [2/4] Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERRO ao instalar dependencias.
    pause
    exit /b 1
)

echo.
echo [3/4] Instalando PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo ERRO ao instalar PyInstaller.
    pause
    exit /b 1
)

echo.
echo [4/4] Compilando executavel...
python -m PyInstaller ^
    --name="CRAWL TV EVANGELIZAR" ^
    --onefile ^
    --windowed ^
    --add-data="config.json;." ^
    --add-data="quotes_history.json;." ^
    --add-data="index.html;." ^
    --clean ^
    --noconfirm ^
    app.py

if errorlevel 1 (
    echo.
    echo ==========================================
    echo   ERRO: Compilacao falhou.
    echo ==========================================
    pause
    exit /b 1
)

if exist "dist\CRAWL TV EVANGELIZAR.exe" (
    echo.
    echo ==========================================
    echo   SUCESSO!
    echo ==========================================
    echo.
    echo Executavel: dist\CRAWL TV EVANGELIZAR.exe
    echo.
    echo Para usar:
    echo   1. Copie a pasta "dist" para onde quiser
    echo   2. Clique duplo em "CRAWL TV EVANGELIZAR.exe"
    echo   3. O navegador abrira automaticamente
    echo   4. Acesse de outras maquinas pelo IP da rede
    echo.
) else (
    echo.
    echo ==========================================
    echo   ERRO: Executavel nao foi gerado.
    echo ==========================================
)

echo.
pause
