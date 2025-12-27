#!/bin/bash

#python manage.py "${SERVER_ROLE}"
python manage.py collectstatic;
/usr/local/bin/gunicorn config.asgi -k config.my_uvicorn_worker.MyUvicornWorker --bind="0.0.0.0:${PORT}" --chdir=/app --timeout "${SERVER_TIMEOUT}" --log-level=debug --threads 8;
