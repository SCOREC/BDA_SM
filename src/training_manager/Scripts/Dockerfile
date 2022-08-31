FROM ubuntu:latest
#FROM python:3.9.13-alpine3.16
#FROM tensorflow/build:2.11-python3.9
RUN adduser --disabled-password training_manager

WORKDIR /home/training_manager

COPY training_manager/requirements.txt requirements.txt
#RUN apk add --no-cache python3 py3-numpy 
RUN apt-get -y update && apt-get -y upgrade && apt-get -y install python3.10-venv
RUN python3 -m venv venv && venv/bin/pip install --upgrade pip 
RUN venv/bin/pip install --upgrade -r requirements.txt

COPY --chown=training_manager:training_manager training_manager/server server
COPY --chown=training_manager:training_manager trainer trainer

COPY --chown=training_manager:training_manager training_manager/training_manager.py training_manager/Scripts/boot.sh ./
RUN chmod +x boot.sh

USER training_manager
EXPOSE 5000
ENTRYPOINT ["/home/training_manager/boot.sh"]
