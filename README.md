
REST API для управления заказами в ресторане. Написан на FastAPI с асинхронной базой данных.

## Стек технологий

 Python 3.11+
 
 FastAPI - асинхронный веб-фреймворк
 
 SQLAlchemy 2.0 - ORM для работы с базой данных
 
 Pydantic - валидация данных и типизация
 
 Asyncio - асинхронное программирование
 
 SQLite - база данных (в продакшене PostgreSQL)

## Функциональность

 Создание заказа (POST /orders)
 
 Получение всех заказов (GET /orders)
 
 Получение заказа по ID (GET /orders/{id})
 
 Обновление статуса заказа (PATCH /orders/{id}/status)
 
 Автоматическая валидация данных через Pydantic
 
 Правильные HTTP статус-коды (201, 404, 422)
 
 Асинхронные запросы к базе данных
 
 Dependency Injection для управления сессиями БД

## Установка и запуск

1. Клонируйте репозиторий: git clone [https://github.com/lastr1ot/restaurant-api.git](https://github.com/lastr1ot/restaurant-api.git) cd restaurant-api
2. Создайте виртуальное окружение и установите зависимости: python3 -m venv venv source venv/bin/activate pip install -r requirements.txt
3. Запустите сервер: uvicorn main:app --reload
4. Откройте Swagger документацию: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Структура проекта

- main.py - FastAPI приложение и эндпоинты
- models.py - Pydantic модели для валидации
- database.py - SQLAlchemy ORM модели
- requirements.txt - Зависимости проекта
- README.md - Документация

## API Эндпоинты

POST /orders - Создать новый заказ 

GET /orders - Получить все заказы

GET /orders/{id} - Получить заказ по ID

PATCH /orders/{id}/status - Обновить статус заказа

## Автор

Роман Чичерин 
GitHub: github.com/lastr1ot
