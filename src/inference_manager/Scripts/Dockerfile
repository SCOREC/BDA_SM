FROM ubuntu:22.04
RUN useradd -ms /bin/bash inference_manager

WORKDIR /home/inference_manager

COPY inference_manager/requirements.txt requirements.txt
RUN apt-get -y update && apt-get -y upgrade && apt-get -y install python3.10-venv
RUN python3 -m venv venv && venv/bin/pip install --upgrade pip 
RUN venv/bin/pip install --upgrade -r requirements.txt

COPY --chown=inference_manager:inference_manager inference_manager/server server
COPY --chown=inference_manager:inference_manager analyzers analyzers
RUN rm -f analyzers/common
COPY --chown=inference_manager:inference_manager common common
RUN ln -s common analyzers/common

COPY --chown=inference_manager:inference_manager inference_manager/inference_manager.py inference_manager/Scripts/boot.sh ./
RUN chmod +x boot.sh

USER inference_manager
EXPOSE 5000
ENTRYPOINT ["/home/inference_manager/boot.sh"]
