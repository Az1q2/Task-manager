# Task-manager



Современное приложение для управления задачами, построенное на базе FastAPI и PostgreSQL.



### Стек технологий:

**Backend**: Python 3.14, FastAPI

**Database**: PostgreSQL

**ORM**: SQLAlchemy (async), но на данный момент только sync

**Migrations**: Alembic

**Package Manager**: uv

**Containerization**: Docker & Docker Compose, но пока api не поднимается docker

**Frontend**: HTML, CSS (Jinja2 templates)



## Быстрый старт

1. Устанавливаем uv, если его ещё нет:  
```curl -LsSf https://astral.sh/uv/install.sh | sh```
  
2. Установка окружения и зависимостей:  
```uv sync```


## Пример окружения .env



```
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
DB_NAME=
```
## Миграции Alembic



1. Создание миграции  
`uv run alembic revision --autogenerate -m "Описание"`
2. Применение миграций  
`uv run alembic upgrade head`

## Структура ORM моделей



Модели данных спроектированы с использованием движка SQLAlchemy. 

### Основные сущности:

**User**: 
![img_2.png](img_2.png)

**Task**: 
![img_1.png](img_1.png)

## Frontend 




**HTML**: Шаблоны находятся в папке src/templates и используют синтаксис Jinja2.

**CSS**: Стили находятся в src/static/css.

## Docker Compose



Для запуска всей инфраструктуры (приложение + база данных) одной командой, но пока запускается только база данных(:  
`docker-compose up --build` 

### Сервисы в compose:

**db**: Образ postgres:latest.

**app**: Контейнер с FastAPI