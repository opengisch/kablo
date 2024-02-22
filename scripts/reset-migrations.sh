#!/usr/bin/env bash


find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete

docker compose exec kablo python manage.py makemigrations
docker compose exec kablo python manage.py migrate
