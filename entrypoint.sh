#!/bin/sh
set -e

if [ -n "${DB_HOST:-}" ]; then
  echo "Waiting for MySQL..."
  until nc -z ${DB_HOST} ${DB_PORT:-3306}; do
    sleep 2
  done
fi

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Starting Gunicorn..."
exec gunicorn ${DJANGO_SERVICE}.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-2}" \
  --timeout 60 \
  --access-logfile - \
  --error-logfile -
