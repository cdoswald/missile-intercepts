FROM continuumio/miniconda3

WORKDIR /app

RUN conda config --add channels defaults
RUN conda config --add channels conda-forge
RUN conda update conda

COPY /docs/env/environment.yml ./docs/env/environment.yml

RUN conda env create -f ./docs/env/environment.yml --platform linux-64

SHELL ["conda", "run", "-n", "missile_env", "/bin/bash", "-c"]

COPY . .