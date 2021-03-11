#!/bin/sh
source venv/bin/activate
echo $PATH
rm -f authServer.db
rm -rf migrations
flask db init
flask db migrate
flask db upgrade
python testingscript.py

exec gunicorn -b 0.0.0.0:5000  --access-logfile - --error-logfile -  authServer:app
