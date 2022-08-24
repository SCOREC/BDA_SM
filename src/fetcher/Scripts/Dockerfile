FROM continuumio/miniconda3

RUN adduser --disabled-password fetcher

WORKDIR /home/fetcher

COPY requirements.txt requirements.txt
RUN conda init zsh
RUN conda create --name venv python=3.9
RUN conda install -c conda-forge -n venv --file requirements.txt  \
    && /opt/conda/bin/conda clean -afy \
    && find /opt/conda/ -follow -type f -name '*.a' -delete \
    && find /opt/conda/ -follow -type f -name '*.pyc' -delete \
    && find /opt/conda/ -follow -type f -name '*.js.map' -delete 

COPY --chown=fetcher:fetcher server server
COPY --chown=fetcher:fetcher fetcher.py Scripts/boot.sh ./


USER fetcher
RUN conda init --all
EXPOSE 5000
ENTRYPOINT ["/home/fetcher/boot.sh"]
