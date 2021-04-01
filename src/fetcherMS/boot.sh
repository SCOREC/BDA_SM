#!/bin/sh
source venv/bin/activate
echo $PATH
pytest -v -s

exec gunicorn -b 0.0.0.0:8000  --access-logfile - --error-logfile -  fetcher:app
