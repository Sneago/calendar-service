FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN pip install --no-cache-dir poetry

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root --no-interaction

COPY . .
