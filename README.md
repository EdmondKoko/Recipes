# Foodgram - Сервис рецептов

### Этот сервис предназначен для публикации рецептов, подписок на других пользователей,добавления понравившихся рецептов в список “Избранное” и “Список покупок”, а также для скачивания сводного списка продуктов.

![example workflow](https://github.com/EdmondKoko/foodgram-project-react/blob/master/.github/workflows/main.yml)

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python&logoColor=yellow)
![Django](https://img.shields.io/badge/Django-3.2.18-red?style=for-the-badge&logo=django&logoColor=blue)
![Postgres](https://img.shields.io/badge/Postgres-13.0-blueviolet?style=for-the-badge&logo=postgresql&logoColor=yellow)
![Nginx](https://img.shields.io/badge/NGINX-1.21.3-orange?style=for-the-badge&logo=nginx&logoColor=green)


## Как развернуть проект на удаленном сервере:
 - Клонировать репозиторий:
git@github.com:EdmondKoko/foodgram-project-react.git
 - Установить на сервере Docker и Docker Compose:
https://docs.docker.com/compose/install/
 - Скопировать на сервер файлы docker-compose.yml, nginx.conf:
scp docker-compose.yml nginx.conf username@IP:/home/username/
 - Создать и запустить контейнеры Docker:
sudo docker compose up
 - Выполнить миграции:s
sudo docker compose exec backend python manage.py makemigrations
sudo docker compose exec backend python manage.py migrate
 - Собрать статику:
sudo docker compose exec backend python manage.py collectstatic --noinput
 - Создать суперпользователя:
sudo docker compose exec backend python manage.py createsuperuser
 - Наполнить базу данных:
sudo docker compose exec backend python manage.py loaddata ingredients.json

## Проект доступен по адресу:
http://edmondkoko.servebeer.com/
Login: edmondkoko777@gmail.com
Password: smokimolla7

#### Автор 
 
Трофимов Руслан - [https://github.com/EdmondKoko](https://github.com/EdmondKoko)