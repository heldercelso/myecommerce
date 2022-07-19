#!/usr/bin/env bash
python /code/manage.py makemigrations
python /code/manage.py migrate
echo "yes" | python /code/manage.py collectstatic
exec "$@"