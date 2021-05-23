#!/bin/bash

python manage.py migrate
exec gunicorn -k uvicorn.workers.UvicornWorker --access-logfile - --bind '[::]:8000' --worker-tmp-dir /dev/shm --workers "${GUNICORN_WORKERS:-3}" mailgunner.asgi:application
