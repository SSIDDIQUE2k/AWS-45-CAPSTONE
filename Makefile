PY=python3
MANAGE=$(PY) manage.py

.PHONY: setup migrate run worker beat shell test ingest infra up down dev

setup:
	$(PY) -m venv .venv || true
	. .venv/bin/activate && pip install -U pip && pip install -r requirements.txt

migrate:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

run:
	daphne -b 0.0.0.0 -p 8000 config.asgi:application

worker:
	celery -A config.celery:app worker -l info

beat:
	celery -A config.celery:app beat -l info

shell:
	$(MANAGE) shell

ingest:
	$(MANAGE) ingest_kb $(PATH)

test:
	pytest -q

infra:
	docker compose up -d db redis

up: migrate
	$(MAKE) run

down:
	docker compose down

dev:
	$(MAKE) infra || true
	$(MANAGE) migrate
	$(MAKE) worker &
	$(MAKE) run
