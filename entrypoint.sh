#!/bin/bash
set -e

export DATABASE_CONN_STR=$(echo $DATABASE_URL | sed 's/postgres/postgresql/g')

if $INIT_DB
then
  python scripts/init-db.py
  python scripts/populate-db.py
fi

gunicorn app_frenzy.app:app -w 4 --bind 0.0.0.0:$PORT -k uvicorn.workers.UvicornWorker --access-logfile -