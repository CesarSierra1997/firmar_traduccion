# 1️⃣ Usa una imagen base con Python y sistema operativo
FROM python:3.11.9

# 2️⃣ Instala dependencias del sistema (LibreOffice y unoconv)
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-core \
    libreoffice-writer \
    libreoffice-common \
    unoconv \
    && apt-get clean

# 3️⃣ Establece el directorio de trabajo en el contenedor
WORKDIR /app

# 4️⃣ Copia los archivos del proyecto al contenedor
COPY . /app/

# 5️⃣ Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# 6️⃣ Recolectar archivos estáticos
RUN python manage.py collectstatic --no-input

# 6️⃣.1 Crea la carpeta media y dale permisos
RUN mkdir -p /app/media && chmod -R 777 /app/media

# 7️⃣ Aplica las migraciones
RUN python manage.py migrate

# 8️⃣ Expone el puerto en el que corre Django
EXPOSE 8000

# 9️⃣ Comando para iniciar el servidor
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "firmar_traduccion.wsgi"]
