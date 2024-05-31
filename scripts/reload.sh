#!/usr/bin/env bash

set -e


DATA=1
MAKE_MIGRATIONS=0
BUILD=

while getopts 'bmn' opt; do
  case "$opt" in
    b)
      echo "-> Rebuild docker image"
      BUILD="--build"
      ;;
    m)
      echo "-> Make migrations"
      MAKE_MIGRATIONS=1
      ;;
    n)
      echo "-> No Data"
      DATA=0
      ;;
    ?|h)
      echo "Usage: $(basename $0) [-bm]"
      exit 1
      ;;
  esac
done

docker compose down -v --remove-orphans || true
docker compose up ${BUILD} -d

if  [[ ${MAKE_MIGRATIONS} -eq 1 ]]; then
  find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
  find . -path "*/migrations/*.pyc"  -delete
  docker compose exec kablo python manage.py makemigrations
fi

docker compose exec kablo python manage.py collectstatic --no-input
docker compose exec kablo python manage.py migrate
docker compose exec kablo python manage.py populate_users
docker compose exec kablo python manage.py populate_valuelists
if  [[ ${DATA} -eq 1 ]]; then
  docker compose exec kablo python manage.py populate_data
fi
