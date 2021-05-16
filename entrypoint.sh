#!/bin/bash
set -e

if $INIT_DB
then
  python scripts/init-db.py
  python scripts/populate-db.py
fi

gunicorn app_frenzy.app:app -w 4 --bind 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker --access-logfile -