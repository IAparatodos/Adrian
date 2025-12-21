#!/bin/bash

echo "🃏 Constructor de Mazos de Commander - MTG"
echo "=========================================="
echo ""

# Verifica si el entorno virtual existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activa el entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instala dependencias si es necesario
if [ ! -f "venv/.installed" ]; then
    echo "📥 Instalando dependencias..."
    pip install -r requirements.txt
    touch venv/.installed
fi

# Inicia el servidor
echo "🚀 Iniciando servidor..."
echo "📡 La aplicación estará disponible en: http://localhost:5000"
echo ""
cd backend
python app.py
