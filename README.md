## Книжная лавка - бесплатная онлайн библиотека.
***
Коммерческая разработка многостраничного сайта на Django с применением современной бэкенд-архитектуры.
***
Для запуска проекта:

Загрузите удаленный репозиторий на ваш ПК, установите зависимости pip install -r requirements.txt;
Создайте S3 хранилище и два бакета в нем: static и media;
Создайте переменные окружения в файле .env в корне проекта и укажите в нем данные для подключения к хранилищу, которые будут использованы в settings.py:
AWS_ACCESS_KEY_ID=ВАШ_КЛЮЧ AWS_SECRET_ACCESS_KEY=ВАШ_СЕКРЕТНЫЙ_КЛЮЧ AWS_S3_ENDPOINT_URL=https://hb.ru-msk.vkcloud-storage.ru AWS_S3_USE_SSL=1 AWS_S3_REGION_NAME=ru-msk

STATIC_BUCKET_NAME=ИМЯ_СТАТИК_БАКЕТА MEDIA_BUCKET_NAME=ИМЯ_МЕДИА_БАКЕТА

USE_S3=1

Проект еще находится на стадии разработки, фронтенд еще не подключен. Также пока используется SQLite для удобства, в продакшене будет использоваться PostgreSQL

Используемые технологии: Django, SQLite, Django ORM, AWS S3, Redis.