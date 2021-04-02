FROM alpine:latest

RUN adduser -D fetcher

WORKDIR /home/fetcher

COPY requirements.txt requirements.txt
RUN apk add --no-cache python3 py3-numpy 
RUN apk add --no-cache --virtual .build-deps gcc g++ zlib-dev make python3-dev  jpeg-dev
RUN python3 -m venv venv
RUN venv/bin/pip install --upgrade pip setuptools wheel
RUN venv/bin/pip install --upgrade -r requirements.txt
RUN apk del .build-deps

COPY fetcher fetcher
COPY tests tests

COPY config.py boot.sh ./
RUN chmod +x boot.sh


ENV FLASK_APP fetcher/__init__.py

RUN chown -R fetcher:fetcher ./

USER fetcher
EXPOSE 8000
ENTRYPOINT ["/home/fetcher/boot.sh"]
