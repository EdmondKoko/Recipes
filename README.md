# Foodgram - Сервис рецептов

### Этот сервис предназначен для публикации рецептов, подписок на других пользователей,добавления понравившихся рецептов в список “Избранное” и “Список покупок”, а также для скачивания сводного списка продуктов.

![workflow status](https://github.com/EdmondKoko/foodgram-project-react/actions/workflows/foodgram-workflow.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python&logoColor=yellow)
![Django](https://img.shields.io/badge/Django-3.2.18-red?style=for-the-badge&logo=django&logoColor=blue)
![Postgres](https://img.shields.io/badge/Postgres-13.0-blueviolet?style=for-the-badge&logo=postgresql&logoColor=yellow)
![Nginx](https://img.shields.io/badge/NGINX-1.21.3-orange?style=for-the-badge&logo=nginx&logoColor=green)


## Как развернуть проект на удаленном сервере:
 - Клонировать репозиторий:

```bash
git@github.com:EdmondKoko/foodgram-project-react.git
```
 - Установить на сервере Docker и Docker Compose:
```bash
https://docs.docker.com/compose/install/
```
 - Скопировать на сервер файлы docker-compose.yml, nginx.conf из папки infra (команды выполнять находясь в папке infra):
```bash
scp docker-compose.yml nginx.conf username@IP:/home/username/
```
 - Создать и запустить контейнеры Docker:
```bash
sudo docker compose up
```
 - Выполнить миграции:
```bash
sudo docker compose exec backend python manage.py makemigrations
```
```bash
sudo docker compose exec backend python manage.py migrate
```
 - Собрать статику:
```bash
sudo docker compose exec backend python manage.py collectstatic --noinput
```
 - Создать суперпользователя:
```bash
sudo docker compose exec backend python manage.py createsuperuser
```
 - Наполнить базу данных:
```bash
sudo docker compose exec backend python manage.py loaddata ingredients.json
```

## После каждого обновления репозитория (push в ветку master) будет происходить:
1. Проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8)
2. Сборка и доставка докер-образов frontend и backend на Docker Hub
3. Разворачивание проекта на удаленном сервере
4. Отправка сообщения в Telegram в случае успеха

## Запуск проекта на локальной машине:
- Клонировать репозиторий:
```git@github.com:EdmondKoko/foodgram-project-react.git```
- В директории infra создать файл .env и заполнить своими данными по аналогии с example.env:
  - DB_ENGINE=django.db.backends.postgresql
  - DB_NAME=postgres
  - POSTGRES_USER=postgres
  - POSTGRES_PASSWORD=postgres
  - DB_HOST=db
  - DB_PORT=5432
  - SECRET_KEY='секретный ключ Django'
- Создать и запустить контейнеры Docker, последовательно выполнить команды по созданию миграций, сбору статики, созданию суперпользователя, как указано выше.

#### Автор 
 
Трофимов Руслан - [https://github.com/EdmondKoko](https://github.com/EdmondKoko)
