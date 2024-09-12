FROM python:3.11-slim

EXPOSE 8002

WORKDIR /opt/app

RUN groupadd -r web && useradd -r -g web web

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./hls_service/requirements.txt requirements.txt
COPY ./hls_service/requirements-prod.txt requirements-prod.txt
COPY ./common_settings ./common_settings

RUN  pip install --upgrade pip && pip install -r requirements.txt -r requirements-prod.txt

COPY ./hls_service/src .
COPY ./cdn ./cdn

USER web
ENTRYPOINT ["gunicorn", "main:app", "--bind", "0.0.0.0:8002", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker"]
