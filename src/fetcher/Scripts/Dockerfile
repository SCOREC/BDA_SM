FROM python:3.9.13-alpine3.16

RUN adduser -D fetcher

WORKDIR /home/fetcher

COPY requirements.txt requirements.txt
#RUN apk add --no-cache cython gcc gfortran
RUN apk add --no-cache --update  python3 python3-dev gcc gfortran musl-dev \
    g++ libffi-dev openssl-dev libxml2 libxml2-dev libxslt libxslt-dev \
    libjpeg-turbo-dev zlib-dev
RUN python3 -m venv venv
RUN venv/bin/pip install --upgrade pip setuptools wheel
RUN venv/bin/pip install --no-cache-dir -r requirements.txt

COPY server server
COPY __init__.py __init__.py 
COPY fetcher.py fetcher.py

COPY Scripts/boot.sh  ./
RUN chmod +x boot.sh 


ENV FLASK_APP fetcher.py

RUN chown -R fetcher:fetcher ./

USER fetcher
EXPOSE 5000
ENTRYPOINT ["/home/fetcher/boot.sh"]
