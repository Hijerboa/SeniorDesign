FROM python:3.8-slim

EXPOSE 5000

WORKDIR /app

RUN apt-get update \
    && apt-get --no-install-recommends -y install gunicorn gcc build-essential tk \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt .

RUN pip install --upgrade pip setuptools wheel

RUN pip install --no-cache-dir -r requirements.txt

COPY app/models /app/

COPY app .

# create unprivileged user
RUN adduser --disabled-password --gecos '' app
