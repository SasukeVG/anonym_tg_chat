FROM python:3.11-slim

COPY requirements.txt opt/app/requirements.txt

WORKDIR /opt/app/

RUN pip install -r requirements.txt

COPY . /opt/app

ENV PYTHONPATH=/opt/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "app/bot/main.py"]
