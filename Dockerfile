FROM python:3.8-slim-buster

EXPOSE 5000

WORKDIR /app

COPY app/requirements.txt .

RUN pip install --upgrade pip setuptools wheel

RUN pip install -r requirements.txt

COPY app/models /app/

RUN apt-get update \
    && apt-get -y install gunicorn \
    && apt-get clean

COPY app .

# create unprivileged user
RUN adduser --disabled-password --gecos '' app

