#!/bin/bash
set -ex
python -m pip install --upgrade pip
pip install -U -r requirements.txt
python manage.py collectstatic --noinput
rm -f db.sqlite3
python manage.py migrate
# python manage.py fixtures
# todo limited perm user in fixtures
python manage.py createsuperuser --username admin@example.com --email admin@example.com  --no-input
python manage.py runserver
