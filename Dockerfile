FROM python:3.11-slim

RUN apt-get update && apt-get install -y libportaudio2 libportaudiocpp0 portaudio19-dev

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]