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

# Run as mamba user
USER $MAMBA_USER

# mamba setup
RUN micromamba shell init --shell=bash --prefix=/micromamba

# Copy setup scripts
COPY setup/install_antismash.sh /deps/
# Copy env files
COPY setup/env_rgi5.yml /deps/
COPY setup/env_natural_product.yml /deps/

# Set up the environments
RUN bash /deps/install_antismash.sh
RUN micromamba env create -f /deps/env_natural_product.yml
RUN micromamba env create -f /deps/env_rgi5.yml
RUN micromamba clean --all --yes

# Set up antibiotic-prediction repo
WORKDIR /antibiotic-prediction
COPY . .

# -----------------------------------------

ENTRYPOINT ["micromamba", "run", "-n", "natural_product" ]

# CMD [ ]
