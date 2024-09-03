FROM python:3.12

RUN mkdir /app

COPY ./requirements.txt /app/requirements.txt
COPY .env /app/.env

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app/src

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN apt-get -y update
RUN apt-get install ffmpeg libsm6 libxext6 -y

COPY ../workers/src /app/
COPY ../cdn/src/ /app/cdn/src/

# DEBUG only - перенос тестового видеофайла в контейнер
#COPY ../cdn/src/media /app/media/

WORKDIR app
