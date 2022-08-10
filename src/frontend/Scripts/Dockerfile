FROM alpine:latest

RUN adduser -D frontend

WORKDIR /home/frontend

COPY requirements.txt requirements.txt
RUN apk add --no-cache python3 py3-numpy 
RUN apk add --no-cache --virtual .build-deps gcc g++ zlib-dev make python3-dev  jpeg-dev
RUN python3 -m venv venv
RUN venv/bin/pip install --upgrade pip setuptools wheel
RUN venv/bin/pip install --upgrade -r requirements.txt
RUN apk del .build-deps

COPY server server
COPY __init__.py __init__.py 
COPY frontend.py frontend.py

COPY Scripts/boot.sh   boot.sh
RUN chmod +x boot.sh


ENV FLASK_APP frontend.py

RUN chown -R frontend:frontend ./

USER frontend
EXPOSE 5000
ENTRYPOINT ["/home/frontend/boot.sh"]
