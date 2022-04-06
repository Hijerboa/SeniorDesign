FROM python:3.8-slim-buster

EXPOSE 5000

WORKDIR /app

RUN apt-get update \
    && apt-get -y install gunicorn python3-dev curl \
    && apt-get clean

RUN apt install apt-transport-https curl gnupg

RUN curl -fsSL https://bazel.build/bazel-release.pub.gpg | gpg --dearmor >bazel-archive-keyring.gpg

RUN mv bazel-archive-keyring.gpg /usr/share/keyrings

RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/bazel-archive-keyring.gpg] https://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list

RUN apt update && sudo apt install bazel

RUN pip install --upgrade pip setuptools wheel

RUN pip install pip numpy wheel packaging

RUN pip install keras_preprocessing --no-deps

# create unprivileged user
RUN adduser --disabled-password --gecos '' app

