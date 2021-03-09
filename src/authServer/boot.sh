#!/bin/sh
source venv/bin/activate
rm -f authServer.db
rm -rf migrations
flask db init
flask db migrate
flask db upgrade
python testingscript.py

exec flask run --host 0.0.0.0 -p 5000