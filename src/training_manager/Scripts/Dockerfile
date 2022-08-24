FROM python:3.9.13-alpine3.16

RUN adduser -D training_manager

WORKDIR /home/training_manager

COPY requirements.txt requirements.txt
RUN apk add --no-cache py3-numpy 
RUN python3 -m venv venv
#RUN venv/bin/pip install --upgrade pip setuptools wheel
RUN venv/bin/pip install --upgrade -r requirements.txt

COPY --chown=training_manager:training_manager server server

COPY --chown=training_manager:training_manager training_manager.py Scripts/boot.sh ./
RUN chmod +x boot.sh

USER training_manager
EXPOSE 5000
ENTRYPOINT ["/home/training_manager/boot.sh"]
