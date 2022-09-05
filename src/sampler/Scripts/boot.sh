#!/bin/bash
source venv/bin/activate

export TRAINER_WORKING_DIRECTORY="./trainer/"
exec gunicorn -b 0.0.0.0:5000  --access-logfile - --error-logfile -  sampler:app
