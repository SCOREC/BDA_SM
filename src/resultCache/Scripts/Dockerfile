FROM python:3.9.13-alpine3.16

RUN adduser -D result_cache

WORKDIR /home/result_cache

COPY requirements.txt requirements.txt
RUN apk add --no-cache py3-numpy 
RUN python3 -m venv venv
#RUN venv/bin/pip install --upgrade pip setuptools wheel
RUN venv/bin/pip install --upgrade -r requirements.txt

COPY --chown=result_cache:result_cache server server

COPY --chown=result_cache:result_cache result_cache.py Scripts/boot.sh ./
RUN chmod +x boot.sh

USER result_cache
EXPOSE 5000
ENTRYPOINT ["/home/result_cache/boot.sh"]
