FROM alpine:latest

RUN adduser -D authServer

WORKDIR /home/authServer

COPY requirements.txt requirements.txt
RUN apk add --no-cache python3 py3-numpy 
RUN apk add --no-cache --virtual .build-deps gcc g++ zlib-dev make python3-dev  jpeg-dev
RUN python3 -m venv venv
RUN venv/bin/pip install --upgrade pip setuptools wheel
RUN venv/bin/pip install --upgrade -r requirements.txt
RUN apk del .build-deps

COPY app app
COPY errors errors
COPY migrations migrations
COPY authServer.py config.py boot.sh testingscript.py .flaskenv ./
RUN chmod +x boot.sh

ENV FLASK_APP authServer.py

RUN chown -R authServer:authServer ./
USER authServer

EXPOSE 5000
ENTRYPOINT ["/home/authServer/boot.sh"]
