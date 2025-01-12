FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt

# Installer les dépendances système nécessaires pour PyAudio
RUN apt-get update && apt-get install -y \
    gcc \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app

CMD ["gunicorn", "app:app"]
