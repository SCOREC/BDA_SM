#!/bin/sh
source venv/bin/activate

#export FLASK_APP=fetcher.py
#exec python fetcher.py
exec gunicorn -b 0.0.0.0:5000  --access-logfile - --error-logfile -  fetcher:app
