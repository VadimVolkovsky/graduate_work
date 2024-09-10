#!/bin/bash

python3 manage.py migrate
python3 manage.py collectstatic --no-input
gunicorn config.wsgi:application --bind 0:8001
