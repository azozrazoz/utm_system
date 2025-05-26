# 🛰 UTM (Unmanned Traffic Management) Система

Веб-приложение для управления беспилотными полётами. Позволяет пилотам регистрироваться, добавлять дронов, создавать маршруты полёта и отправлять их на одобрение оператору. Система также визуализирует запретные зоны на карте и обеспечивает учёт всех разрешений на полёт.

## 🚀 Функционал

- Регистрация и аутентификация пилотов и операторов
- Регистрация дронов
- Создание маршрута с помощью карты (Leaflet Draw)
- Отправка маршрута на одобрение
- Кабинет пилота и кабинет оператора
- Отображение запретных зон (No-Fly Zones) на карте
- Использование Leaflet и Flatpickr для интерактивного интерфейса

## 🛠 Стек технологий

- Python, Django
- PostgreSQL + PostGIS
- Leaflet.js
- Bootstrap 5
- Flatpickr

## 🧭 Установка

1. Клонировать репозиторий:

```bash
git clone https://github.com/azozrazoz/utm-system.git
cd utm-system

pip install -r requirements.txt

CREATE DATABASE utm;
CREATE EXTENSION postgis;

python manage.py migrate
python manage.py runserver
```
