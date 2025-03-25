FROM continuumio/miniconda3

WORKDIR /app

RUN conda config --add channels defaults && \
    conda config --add channels conda-forge && \
    conda update conda

COPY /docs/env/environment.yml ./docs/env/environment.yml
RUN conda env create -f ./docs/env/environment.yml --platform linux-64

RUN conda run -n missile_env pip install pytest

# Activate Conda if interactive mode
RUN echo "source /opt/conda/etc/profile.d/conda.sh && conda activate missile_env" >> ~/.bashrc

# Run commands in Conda if non-interactive mode
SHELL ["conda", "run", "-n", "missile_env", "/bin/bash", "-c"]

COPY . .

RUN pip install -e .