# Verwenden des offiziellen Python-Basisimages von Docker Hub
FROM python:3.8-slim

# Setzen der Arbeitsverzeichnis innerhalb des Containers
WORKDIR /app

# Kopieren der Python-Abhängigkeiten und der .env-Datei in das Arbeitsverzeichnis
COPY requirements.txt ./
COPY .env ./

# Installieren der Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Kopieren des Python-Programms in das Arbeitsverzeichnis
COPY leanix_description.py .

# Exponieren des Ports, den Ihr Flask-Server verwendet (standardmäßig 5000)
EXPOSE 5000

# Definieren des Befehls, um Ihre Flask-Anwendung auszuführen
CMD ["python", "leanix_description.py"]
