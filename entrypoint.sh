#!/bin/sh

# Ожидание готовности базы данных
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"
do
  echo "Ожидание готовности базы данных..."
  sleep 2
done

# Применяем миграции Alembic
alembic upgrade head

# Запускаем приложение
exec python app/bot/main.py  # Замените на вашу команду, если она отличается
