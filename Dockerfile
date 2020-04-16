FROM python:3.7
RUN apt-get update

RUN apt-get install -y \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev

WORKDIR /usr/src/app

COPY requirements*.txt ./
RUN pip install --no-cache-dir \
    -r requirements.txt \
    -r requirements-dev.txt

COPY . .
