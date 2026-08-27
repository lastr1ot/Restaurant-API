FastAPI Orders Service



REST API сервис для управления заказами в ресторане. Проект демонстрирует навыки создания прод бэкенда с правильной архитектурой, кэшированием, очередями задач и полным покрытием тестами.



Описание



Сервис позволяет создавать заказы, отслеживать их статус (новый - готовится - готов) и автоматически отправлять уведомления на кухню через очередь задач. 



Бизнес-сценарии:

\- Официант создаёт заказ - система сохраняет его в БД и ставит задачу на уведомление кухни

\- Повар меняет статус заказа - клиент видит актуальное состояние

\- Система кэширует список заказов для быстрого отображения в меню

\- Rate limiting защищает от DDoS и злоупотреблений



Стек технологий



Backend:

\- Python 3.12, FastAPI, Pydantic V2

\- SQLAlchemy 2.0 (async), Alembic для миграций

\- PostgreSQL 16, Redis 7



Инфраструктура:

\- Docker, Docker Compose

\- arq для асинхронных очередей задач

\- GitHub Actions для CI/CD



Качество кода:

\- pytest + pytest-asyncio (покрытие > 80%)

\- Ruff (линтер + форматтер)

\- httpx, fakeredis для тестирования



Быстрый старт



Локальный запуск



1\. Клонировать репозиторий:

```bash

git clone <твой-репозиторий>

cd fastapi

```



2\. Установить зависимости:

```bash

pip install -r requirements.txt

```



3\. Запустить Redis:

```bash

docker run -d -p 6379:6379 --name redis redis:7

```



4\. Применить миграции БД:

```bash

alembic upgrade head

```



5\. Запустить сервер:

```bash

uvicorn main:app --reload

```



Swagger документация: http://127.0.0.1:8000/docs



Docker Compose



```bash

docker-compose up --build -d

```



API Endpoints



Создание заказа

```bash

POST /orders

Content-Type: application/json



{

"table\_id": 5,

"items": \[

{"name": "Pizza Margherita", "quantity": 2, "price": 450.50},

{"name": "Cola", "quantity": 1, "price": 150.00}

],

"total\_price": 1051.00

}

```



Ответ:

```json

{

"id": 1,

"table\_id": 5,

"items": \[

{"name": "Pizza Margherita", "quantity": 2, "price": 450.50},

{"name": "Cola", "quantity": 1, "price": 150.00}

],

"total\_price": "1051.00",

"status": "new"

}

```



Получение списка заказов

```bash

GET /orders

```

Ответ кэшируется на 60 секунд.



Обновление статуса

```bash

PATCH /orders/1/status?new\_status=cooking

```



Health Check

```bash

GET /health

```



Архитектурные решения



Почему Decimal вместо float?

Для точных финансовых расчётов. Float даёт ошибки округления (0.1 + 0.2 ≠ 0.3), что недопустимо для денег.



Почему JSON для items?

\- Гибкость: можно добавлять поля без миграций

\- Производительность: не нужны JOIN с таблицей OrderItem




Rate Limiting

Middleware ограничивает 10 запросов в минуту с одного IP. Реализовано через Redis (INCR + EXPIRE).



Кэширование

Список заказов кэшируется в Redis на 60 секунд. Инвалидация при создании или обновлении заказа (DEL key).



Очередь задач

arq + Redis для асинхронной отправки уведомлений. Worker запускается отдельным процессом.



Тестирование



Локально

```bash

pytest -v --cov=.

```



В Docker 

```bash

docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

```



Стратегия тестирования:

\- Фикстуры с function-scope для изоляции БД

\- FakeRedis и FakeQueue для мока внешних сервисов

\- Тесты middleware, бизнес-логики, кэширования

\- Параметризация для проверки валидации



CI/CD



GitHub Actions автоматически:

1\. Запускает ruff check и ruff format --check

2\. Запускает pytest в Docker с PostgreSQL

3\. Проверяет exit code



