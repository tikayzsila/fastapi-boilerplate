# Шаблон fastapi проекта
### Включает в себя апи для авторизации, CRUD юзера и роли

- эндпоинты описаны на роуте /docs
- миграции и сидинг запускаются каждый раз при поднятии сервера
- для миграций используется alembic, соответственно чтобы создать миграцию нужно исп. команду 
        ```
        poetry run alembic revision --autogenerate -m "Название миграции"
        ```
- сущности для сидинга описаны в темплейте seed.j2
- Для локального запуска (на linux) нужны:
  - установленный pip, poetry и python 3.10
  - прописать make install
  - создать сертификаты при помощи команды make cert (исп. для подписи jwt токена)
- Для запуска сервера исп. команду
        ```
        make s
        ```
    (для быстрого экспорта используется утилита direnv, для prod используется .env файл)
- Для деплоя используется docker а также .env файл на сервере

## .env файл
> APP_MODULE=boilerplate.main:app
  HOST=0.0.0.0
  PORT=8001
  ENV=dev
  PG_USER=postgres
  PG_PASSWORD=postgres
  PG_DB=myDB
  PG_PORT=5432
  DEFAULT_ADMIN_USERNAME=adm
  DEFAULT_ADMIN_PASSWORD=adm
  PG_HOST=app_db

Переменная ENV отвечает за отображение docs, на прод сервере должно быть значение "prod"
Переменные host и app_module подставляются в команду для запуска приложения