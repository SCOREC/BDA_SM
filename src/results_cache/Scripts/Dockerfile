FROM python:3.9.13-alpine3.16

RUN adduser -D results_cache

WORKDIR /home/results_cache

COPY requirements.txt requirements.txt
RUN apk add --no-cache py3-numpy 
RUN python3 -m venv venv
#RUN venv/bin/pip install --upgrade pip setuptools wheel
RUN venv/bin/pip install --upgrade -r requirements.txt

COPY --chown=results_cache:results_cache server server

COPY --chown=results_cache:results_cache results_cache.py Scripts/boot.sh ./
RUN chmod +x boot.sh

USER results_cache
EXPOSE 5000
ENTRYPOINT ["/home/results_cache/boot.sh"]
