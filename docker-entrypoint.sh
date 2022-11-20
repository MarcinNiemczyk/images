#!/bin/sh
python manage.py makemigrations api
python manage.py migrate
python manage.py loaddata fixtures/builtin_tiers.json
DJANGO_SUPERUSER_PASSWORD=admin python manage.py createsuperuser --no-input --username=admin  --email=admin@example.com