.PHONY:

s:
	poetry run uvicorn \
		--reload \
		--host $$HOST \
		--port $$PORT \
		"$$APP_MODULE"

install:
	poetry env use python3.10 && poetry install --no-root

db:
	docker run --name=TesT-db \
	 			-e SSL_MODE='disable'\
				-e POSTGRES_USER=$$PG_USER\
				-e POSTGRES_PASSWORD=$$PG_PASSWORD\
				-e POSTGRES_DB=$$PG_DB\
				-p $$PG_PORT:5432 -d --rm postgres:alpine

up:
	docker compose up -d --build

# перед апгрейдом нужно создать миграцию командой poetry run alembic revision --autogenerate -m "Название миграции"
migrate:
	poetry run alembic upgrade head

key:
	openssl rand -hex 32