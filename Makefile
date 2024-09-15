DOCKER_COMPOSE:=docker compose
EXEC_ADMIN_PANEL:=$(DOCKER_COMPOSE) exec admin_panel
EXEC_AUTH_API:=$(DOCKER_COMPOSE) exec auth-api
EXEC_WORKER_APP:=$(DOCKER_COMPOSE) exec worker-app


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


# auth-api
migrate_auth:
	$(EXEC_AUTH_API) alembic upgrade head

create_roles:
	$(EXEC_AUTH_API) python src/create_roles.py

create_subscriber:
	$(EXEC_AUTH_API) python src/create_subscriber.py


# worker
create_bucket:
	$(EXEC_WORKER_APP) python create_default_bucket.py


# django utils
createsuperuser:
	$(EXEC_ADMIN_PANEL) ./manage.py createsuperuser

runserver:
	$(EXEC_ADMIN_PANEL) ./manage.py runserver

makemigrations:
	$(EXEC_ADMIN_PANEL) ./manage.py makemigrations

makemigrations-merge:
	$(EXEC_ADMIN_PANEL) ./manage.py makemigrations --merge

migrate:
	$(EXEC_ADMIN_PANEL) ./manage.py migrate

makemessages:
	$(EXEC_ADMIN_PANEL) ./manage.py makemessages

compilemessages:
	$(EXEC_ADMIN_PANEL) ./manage.py compilemessages

shell:
	$(EXEC_ADMIN_PANEL) bash


# helpers

flake8:
	$(EXEC_ADMIN_PANEL) flake8

flake8-hook:
	flake8 --install-hook git
	git config --bool flake8.strict true

isort:
	$(EXEC_ADMIN_PANEL) isort -rc backend_api

test:
	$(EXEC_ADMIN_PANEL) ./run_tests.sh

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
