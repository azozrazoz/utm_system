FROM python:3.11-slim

# Установка зависимостей ОС
RUN apt-get update && apt-get install -y \
    binutils libproj-dev gdal-bin libgdal-dev \
    gcc python3-dev musl-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV GDAL_VERSION=3.6.2

# Создание рабочей директории
WORKDIR /code

# Установка Python-зависимостей
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY app /code