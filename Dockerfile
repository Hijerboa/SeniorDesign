FROM python:3.8-slim-buster

EXPOSE 5000

WORKDIR /app

RUN apt-get update \
    && apt-get -y install netcat gcc default-libmysqlclient-dev libpq-dev python-dev gunicorn\
    && apt-get clean \

RUN apt remove rustc

RUN curl https://sh.rustup.rs 15 -sSf -y | sh

RUN export CRYPTOGRAPHY_DONT_BUILD_RUST=1

COPY app/requirements.txt /app

RUN pip install --upgrade pip setuptools wheel

RUN pip install -r requirements.txt

COPY app ./

# create unprivileged user
RUN adduser --disabled-password --gecos '' app

