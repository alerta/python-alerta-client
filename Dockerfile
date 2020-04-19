FROM python:3.8-alpine

RUN apk add --no-cache \
    bash \
    build-base \
    libffi-dev \
    openssl-dev \
    postgresql-dev \
    python3-dev

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt
RUN pip install .
