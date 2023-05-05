.PHONY:

s:
	poetry run uvicorn \
		--reload \
		--host $$HOST \
		--port $$PORT \
		"$$APP_MODULE"

install:
	poetry env use python3.11 && poetry install --no-root

db:
	docker run --name=TesT-db \
	 			-e SSL_MODE='disable'\
				-e POSTGRES_USER=$$PG_USER\
				-e POSTGRES_PASSWORD=$$PG_PASSWORD\
				-e POSTGRES_DB=$$PG_DB\
				-e TZ=GMT-3\
				-p $$PG_PORT:5432 -d --rm postgres:alpine

# перед апгрейдом нужно создать миграцию командой poetry run alembic revision --autogenerate -m "Название миграции"
migrate:
	poetry run alembic upgrade head

c:
	py3clean .
