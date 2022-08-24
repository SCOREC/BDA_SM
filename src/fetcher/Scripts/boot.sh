#!/bin/bash --login
conda activate venv

export FLASK_APP=fetcher.py
exec gunicorn -b 0.0.0.0:5000  --access-logfile - --error-logfile -  fetcher:app
