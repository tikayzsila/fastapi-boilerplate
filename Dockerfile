FROM python:3.10.9-slim as base

ARG APP_NAME=app
ARG APP_PATH=/opt/$APP_NAME
WORKDIR $APP_PATH
ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1

FROM base as builder

COPY pyproject.toml poetry.lock ./
RUN pip install poetry
COPY . .
RUN poetry build --format wheel
RUN poetry export --format requirements.txt --output constraints.txt --without-hashes --without dev

FROM python:3.10.9-slim

ARG APP_NAME=app
ARG APP_PATH=/opt/$APP_NAME
WORKDIR $APP_PATH

RUN useradd serve && groupadd -r prod && chown serve:prod $APP_PATH
COPY --from=builder --chown=serve:prod $APP_PATH/dist/*.whl ./
COPY --from=builder --chown=serve:prod $APP_PATH/constraints.txt ./

RUN pip install *.whl --constraint constraints.txt && rm *.txt *.whl
RUN chmod ugo-rwx -R /usr/bin && chmod ugo-rwx -R /bin

USER serve