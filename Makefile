DOCKER_COMPOSE:=docker-compose
EXEC_CORE:=$(DOCKER_COMPOSE) exec admin_panel


# work with docker

build:
# 	export DOCKER_BUILDKIT=1 && docker build -f docker/Dockerfile -t movies_django_movie .
	$(DOCKER_COMPOSE) build

ps:
	$(DOCKER_COMPOSE) ps

up:
	$(DOCKER_COMPOSE) up

restart:
	$(DOCKER_COMPOSE) restart

down:
	$(DOCKER_COMPOSE) down

pull:
	$(DOCKER_COMPOSE) pull


# django utils
createsuperuser:
	$(EXEC_CORE) ./manage.py createsuperuser

runserver:
	$(EXEC_CORE) ./manage.py runserver

makemigrations:
	$(EXEC_CORE) ./manage.py makemigrations

makemigrations-merge:
	$(EXEC_CORE) ./manage.py makemigrations --merge

migrate:
	$(EXEC_CORE) ./manage.py migrate

makemessages:
	$(EXEC_CORE) ./manage.py makemessages

compilemessages:
	$(EXEC_CORE) ./manage.py compilemessages

shell:
	$(EXEC_CORE) bash


# helpers

flake8:
	$(EXEC_CORE) flake8

flake8-hook:
	flake8 --install-hook git
	git config --bool flake8.strict true

isort:
	$(EXEC_CORE) isort -rc backend_api

test:
	$(EXEC_CORE) ./run_tests.sh

upgrade-requirements:
	$(DOCKER_COMPOSE) run core \
		/bin/bash -c 'pip uninstall workout-recommendation -y && pip freeze | xargs pip uninstall -y && pip install -U -r /app/requirements-dev.txt && /app/freeze.sh'
	$(DOCKER_COMPOSE) build

install-requirements:
	$(DOCKER_COMPOSE) run core \
		/bin/bash -c 'pip install -r /app/requirements.txt'
	$(DOCKER_COMPOSE) build

remove-merged-branches:
	git branch --merged | egrep -v "(^\*|master|prod)" | xargs git branch -d
