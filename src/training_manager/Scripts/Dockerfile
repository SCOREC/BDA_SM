FROM python:3.8-slim 

RUN apt update && \
    apt install --no-install-recommends -y build-essential python3-venv

RUN useradd -ms /bin/bash training_manager
WORKDIR /home/training_manager

COPY training_manager/requirements.txt requirements.txt
RUN python3 -m venv venv && venv/bin/pip install --upgrade pip 
RUN venv/bin/pip install --upgrade -r requirements.txt

COPY --chown=training_manager:training_manager training_manager/server server
COPY --chown=training_manager:training_manager common common
COPY --chown=training_manager:training_manager trainer trainer

COPY --chown=training_manager:training_manager training_manager/training_manager.py training_manager/Scripts/boot.sh ./
RUN chmod +x boot.sh

USER training_manager
EXPOSE 5000
ENTRYPOINT ["/home/training_manager/boot.sh"]
