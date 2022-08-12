FROM python:3.9.13-alpine3.16

RUN adduser -D fetcher

WORKDIR /home/fetcher

COPY requirements.txt requirements.txt
RUN apk add --no-cache py3-numpy 
RUN python3 -m venv venv
RUN venv/bin/pip install --upgrade pip setuptools wheel
RUN venv/bin/pip install --upgrade -r requirements.txt

COPY server server

COPY fetcher.py ./
COPY Scripts/boot.sh ./
RUN chmod +x boot.sh


ENV FLASK_APP fetcher.py

RUN chown -R fetcher:fetcher ./

USER fetcher
EXPOSE 5000
ENTRYPOINT ["/home/fetcher/boot.sh"]
