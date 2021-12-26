FROM python:3.8-slim-buster

EXPOSE 5000

WORKDIR /app

COPY app ./

RUN pip install --upgrade pip setuptools wheel

RUN ls

RUN pip install -r requirements.txt

RUN apt-get update \
    && apt-get -y install netcat gcc gunicorn \
    && apt-get clean

# create unprivileged user
RUN adduser --disabled-password --gecos '' app

