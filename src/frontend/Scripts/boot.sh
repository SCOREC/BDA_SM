#!/bin/sh
source venv/bin/activate
rm -f server/databases/*.db

exec gunicorn -b 0.0.0.0:5000  --access-logfile - --error-logfile -  frontend:app
