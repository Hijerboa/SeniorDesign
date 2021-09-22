FROM python:3.8-slim-buster

WORKDIR /app

RUN apt-get update \
    && apt-get -y install netcat gcc libpq-dev python-dev\
    && apt-get clean

COPY ./app/requirements.txt /app
RUN pip install -r requirements.txt

COPY ./app ./

# create unprivileged user
RUN adduser --disabled-password --gecos '' app