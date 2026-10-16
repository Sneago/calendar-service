# Calendar Service

## Запуск в Docker

```bash
cp .env.example .env
docker compose up --build
```

Swagger: http://localhost:8000/api/docs/

## Запуск без Docker

Нужны Python 3.14, poetry и Postgres.

1. Создать пользователя и базу:

   ```bash
   psql -d postgres -c "CREATE USER calendar WITH PASSWORD 'calendar'" -c "CREATE DATABASE calendar OWNER calendar"
   ```

2. `cp .env.example .env`, в `.env` заменить `POSTGRES_HOST=db` на `POSTGRES_HOST=localhost`.
3. Установить зависимости, применить миграции и запустить:

   ```bash
   poetry install
   poetry run python manage.py migrate
   poetry run python manage.py runserver
   ```
