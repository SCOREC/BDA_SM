#!/bin/bash
source venv/bin/activate

export TRAINER_WORKING_DIRECTORY="./trainer/"
export RESULTS_CACHE_URL="http://172.18.29.173:5002"
export TRAINING_MANAGER_PORT=5000
exec python3 training_manager.py
#exec gunicorn -b 0.0.0.0:5000  --access-logfile - --error-logfile -  training_manager:app
