FROM python:3.9.13-alpine3.16

RUN adduser -D frontend

WORKDIR /home/frontend

COPY requirements.txt requirements.txt
RUN python3 -m venv venv
RUN venv/bin/pip install --upgrade pip setuptools wheel
RUN venv/bin/pip install --upgrade -r requirements.txt

COPY server server
COPY __init__.py __init__.py 
COPY frontend.py frontend.py

COPY Scripts/boot.sh   Scripts/remake.sh ./
RUN chmod +x boot.sh remake.sh


ENV FLASK_APP frontend.py

RUN chown -R frontend:frontend ./

USER frontend
EXPOSE 5000
ENTRYPOINT ["/home/frontend/boot.sh"]
