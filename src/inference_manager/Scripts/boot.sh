#!/bin/bash
source venv/bin/activate

export ANALYZERS_WORKING_DIRECTORY="./analyzers"
exec gunicorn -b 0.0.0.0:5000  --access-logfile - --error-logfile -  inference_manager:app
