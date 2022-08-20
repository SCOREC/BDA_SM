FROM python:3.9.13-alpine3.16

RUN adduser -D fetcher

WORKDIR /home/training_manager

COPY requirements.txt requirements.txt
RUN apk add --no-cache py3-numpy 
RUN python3 -m venv venv
RUN venv/bin/pip install --upgrade pip setuptools wheel
RUN venv/bin/pip install --upgrade -r requirements.txt

COPY server server

COPY training_manager.py ./
COPY Scripts/boot.sh ./
RUN chmod +x boot.sh


ENV FLASK_APP training_manager.py

RUN chown -R training_manager:training_manager ./

USER training_manager
EXPOSE 5000
ENTRYPOINT ["/home/fetcher/boot.sh"]
