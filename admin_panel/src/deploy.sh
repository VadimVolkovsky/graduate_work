#!/bin/bash

python3 manage.py collectstatic --noinput
python3 manage.py migrate
gunicorn config.wsgi:application --bind 0:8001
