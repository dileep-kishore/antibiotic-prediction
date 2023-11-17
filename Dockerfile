FROM mambaorg/micromamba

# metadata
LABEL software="antibiotic-prediction"
LABEL version="0.1.0"

LABEL authors.name="Dileep Kishore"
LABEL authors.email="kishored@ornl.gov"

# Run as root
USER root

RUN apt-get update && apt-get -y upgrade \
  && apt-get install -y --no-install-recommends \
  git \
  wget \
  g++ \
  ca-certificates \
  apt-transport-https \
  gnupg \
  && rm -rf /var/lib/apt/lists/*


# Create directories
RUN mkdir /deps && chown $MAMBA_USER:$MAMBA_USER /deps
RUN mkdir /antibiotic-prediction && chown $MAMBA_USER:$MAMBA_USER /antibiotic-prediction

ENV MAMBA_ROOT_PREFIX="~/micromamba"
# Run as mamba user
USER $MAMBA_USER

# mamba setup
RUN micromamba shell init --shell=bash --prefix=~/micromamba

# Copy setup scripts
COPY --chown=$MAMBA_USER:$MAMBA_USER setup/install_antismash.sh /deps/
COPY --chown=$MAMBA_USER:$MAMBA_USER setup/install_rgi.sh /deps/
# Copy env files
COPY --chown=$MAMBA_USER:$MAMBA_USER setup/env_natural_product.yml /deps/
# COPY setup/env_rgi5.yml ~/deps/

# Set up the environments for antibiotic prediction
RUN bash /deps/install_antismash.sh
RUN bash /deps/install_rgi.sh
RUN micromamba env create -f /deps/env_natural_product.yml
# RUN micromamba env create -f /deps/env_rgi5.yml

# Set up environment for resistance prediction
COPY --chown=$MAMBA_USER:$MAMBA_USER setup/env_resistance_prediction.yml /deps/
RUN micromamba env create -f /deps/env_resistance_prediction.yml

# Clean up
RUN micromamba clean --all --yes

# Set up antibiotic-prediction repo
USER root
RUN mkdir /outputs && chown $MAMBA_USER:$MAMBA_USER /outputs
USER $MAMBA_USER
WORKDIR /antibiotic-prediction
COPY . .
WORKDIR /antibiotic-prediction/antibiotic_prediction

# -----------------------------------------
ENTRYPOINT [ "/usr/local/bin/_entrypoint.sh" ]
# ENTRYPOINT ["micromamba", "run", "-n", "natural_product" ]

# CMD [ ]
