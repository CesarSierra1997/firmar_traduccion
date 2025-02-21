#!/usr/bin/env bash
# exit on error
set -o errexit

# Instalar LibreOffice y verificar instalación
apt-get update && apt-get install -y libreoffice libreoffice-core libreoffice-writer libreoffice-common unoconv
libreoffice --version || echo "⚠ LibreOffice no está disponible"

# Instalar dependencias de Python
pip install -r requirements.txt

# Recolectar archivos estáticos
python manage.py collectstatic --no-input

# Aplicar migraciones
python manage.py migrate
