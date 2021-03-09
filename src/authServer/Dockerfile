FROM python:3.6-alpine

RUN adduser -D authServer

WORKDIR /home/authServer

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt

COPY app app
COPY errors errors
COPY migrations migrations
COPY authServer.py config.py boot.sh testingscript.py .flaskenv ./
RUN chmod +x boot.sh

ENV FLASK_APP authServer.py

RUN chown -R authServer:authServer ./
USER authServer

EXPOSE 5000
ENTRYPOINT [ "./boot.sh" ]