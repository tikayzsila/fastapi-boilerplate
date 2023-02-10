.PHONY:

s:
	poetry run uvicorn \
		--reload \
		--host $$HOST \
		--port $$PORT \
		"$$APP_MODULE"

install:
	poetry env use python3.10 && poetry install --no-root
