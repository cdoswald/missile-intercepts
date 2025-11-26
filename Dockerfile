FROM mambaorg/micromamba

# Install packages
COPY environment.yml ./environment.yml
RUN micromamba install -y -n base -f ./environment.yml && micromamba clean --all

# Copy source code into app folder
WORKDIR /app
COPY . .

# Add permissions to mamba user
USER root
RUN chown -R $MAMBA_USER:$MAMBA_USER /app
USER $MAMBA_USER

# Install source code as package
RUN micromamba run -n base pip install -e .