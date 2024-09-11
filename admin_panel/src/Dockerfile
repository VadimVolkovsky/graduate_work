FROM python:3.12

RUN mkdir /app

COPY manage.py /app/manage.py
COPY deploy.sh /app/deploy.sh
COPY requirements.txt /app/requirements.txt

RUN  pip install --upgrade pip \
     && pip install -r /app/requirements.txt --no-cache-dir


WORKDIR /app
COPY . /app

RUN chmod +x /app/deploy.sh

CMD /app/deploy.sh
