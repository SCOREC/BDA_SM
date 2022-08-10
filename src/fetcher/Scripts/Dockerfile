FROM python:3.9.13-alpine3.16

RUN adduser -D fetcher

WORKDIR /home/fetcher

COPY requirements.txt requirements.txt
RUN apk add --no-cache py3-numpy 
#RUN apk add --no-cache --virtual .build-deps gcc g++ zlib-dev make python3-dev  jpeg-dev
RUN python3 -m venv venv
RUN venv/bin/pip install --upgrade pip setuptools wheel
RUN venv/bin/pip install --upgrade -r requirements.txt
#RUN apk del .build-deps

COPY api api
COPY tests tests

COPY config.py Scripts/boot.sh ./
RUN chmod +x boot.sh


ENV FLASK_APP api/__init__.py

RUN chown -R fetcher:fetcher ./

USER fetcher
EXPOSE 8000
ENTRYPOINT ["/home/fetcher/boot.sh"]
