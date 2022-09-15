FROM python:3.8-slim 
RUN apt update && \
    apt install --no-install-recommends -y build-essential python3-venv

RUN useradd -ms /bin/bash sampler
WORKDIR /home/sampler

RUN python3 -m venv venv && venv/bin/pip install --upgrade pip 
COPY sampler/requirements.txt requirements.txt
RUN venv/bin/pip install --no-cache-dir -r requirements.txt

COPY --chown=sampler:sampler sampler/server server
COPY --chown=sampler:sampler common common

COPY --chown=sampler:sampler sampler/sampler.py sampler/Scripts/boot.sh ./
RUN chmod +x boot.sh

USER sampler
EXPOSE 5000
ENTRYPOINT ["/home/sampler/boot.sh"]
