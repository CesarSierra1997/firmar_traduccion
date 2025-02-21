#!/usr/bin/env bash
# exit on error
set -o errexit

# Instalar Unoconv
apt-get update && apt-get install -y unoconv

# Instalar dependencias de Python
pip install -r requirements.txt

# Recolectar archivos estáticos
python manage.py collectstatic --no-input

# Aplicar migraciones
python manage.py migrate
