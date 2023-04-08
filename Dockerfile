FROM python:3.10.10-alpine3.17 as base

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
RUN poetry export --format requirements.txt --output requirements.txt --without-hashes --without dev

FROM python:3.10.10-alpine3.17

ARG APP_NAME=app
ARG APP_PATH=/opt/$APP_NAME
WORKDIR $APP_PATH

RUN apk update && apk add shadow tzdata &&\
     groupadd -g 1001 serve &&\
     useradd -u 1001 -g 1001 serve &&\
     cp /usr/share/zoneinfo/Europe/Moscow /etc/localtime && echo "Europe/Moscow" > /etc/timezone && \
     apk del tzdata shadow &&\
     mkdir $APP_PATH/static &&\
        chown -R serve:serve $APP_PATH

ENV LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8
ENV TZ="Europe/Moscow"

COPY --from=builder --chown=serve:serve $APP_PATH/dist/*.whl \ 
                    $APP_PATH/requirements.txt \
                    $APP_PATH/migrations \
                    $APP_PATH/alembic.ini \
                    $APP_PATH/logger.conf \
                    $APP_PATH/seed.j2 ./

COPY --from=builder --chown=serve:serve $APP_PATH/migrations $APP_PATH/migrations

RUN pip install *.whl -r requirements.txt && rm *.txt *.whl
USER serve

