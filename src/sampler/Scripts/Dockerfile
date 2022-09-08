FROM ubuntu:latest
RUN useradd -ms /bin/bash sampler

WORKDIR /home/sampler

COPY sampler/requirements.txt requirements.txt
RUN apt-get -y update && apt-get -y upgrade && apt-get -y install python3.10-venv
RUN python3 -m venv venv && venv/bin/pip install --upgrade pip 
RUN venv/bin/pip install --upgrade -r requirements.txt

COPY --chown=sampler:sampler sampler/server server
COPY --chown=sampler:sampler common common

COPY --chown=sampler:sampler sampler/sampler.py sampler/Scripts/boot.sh ./
RUN chmod +x boot.sh

USER sampler
EXPOSE 5000
ENTRYPOINT ["/home/sampler/boot.sh"]
