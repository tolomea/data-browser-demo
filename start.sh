#!/bin/bash
set -ex
python -m pip install --upgrade pip
pip install -U -r requirements.txt
python manage.py collectstatic --noinput
rm -f db.sqlite3
python manage.py migrate
python manage.py fixtures
