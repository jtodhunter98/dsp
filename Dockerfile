FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN apt-get update && apt-get install -y python3-dev default-libmysqlclient-dev build-essential

COPY ./app/requirements.txt /app

RUN pip install -r requirements.txt

COPY ./app /app