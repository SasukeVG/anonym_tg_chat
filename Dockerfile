FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Установка Python-зависимостей
WORKDIR /opt/app/
COPY requirements.txt .
# Копируем файл requirements.txt в рабочую директорию
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini /opt/app/alembic.ini


# Настройки окружения
ENV PYTHONPATH=/opt/app
ENV PYTHONUNBUFFERED=1

# Копируем и настраиваем скрипт entrypoint.sh
COPY entrypoint.sh /opt/app/entrypoint.sh
RUN chmod +x /opt/app/entrypoint.sh

# Устанавливаем команду запуска
CMD ["/opt/app/entrypoint.sh"]
