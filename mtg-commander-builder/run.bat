@echo off
echo 🃏 Constructor de Mazos de Commander - MTG
echo ==========================================
echo.

REM Verifica si el entorno virtual existe
if not exist "venv\" (
    echo 📦 Creando entorno virtual...
    python -m venv venv
)

REM Activa el entorno virtual
echo 🔧 Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instala dependencias si es necesario
if not exist "venv\.installed" (
    echo 📥 Instalando dependencias...
    pip install -r requirements.txt
    type nul > venv\.installed
)

REM Inicia el servidor
echo 🚀 Iniciando servidor...
echo 📡 La aplicación estará disponible en: http://localhost:5000
echo.
cd backend
python app.py
