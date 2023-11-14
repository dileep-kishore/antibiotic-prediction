FROM mambaorg/micromamba

# metadata
LABEL software="antibiotic-prediction"
LABEL version="0.1.0"

MAINTAINER name="Dileep Kishore" email="kishored@ornl.gov"

USER 0
RUN apt-get update && apt-get -y upgrade \
  && apt-get install -y --no-install-recommends \
  git \
  wget \
  g++ \
  ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# mamba setup
RUN micromamba shell init --shell=bash --prefix=~/micromamba

# Copy setup scripts
COPY setup/install_antismash.sh /deps/
COPY setup/install_rgi.sh /deps/
COPY setup/install_natural_product.sh /deps/

# Copy env
COPY setup/env_rgi5.yml /deps/
COPY setup/env_natural_product.yml /deps/

# Run setup scripts
# TODO: Replace antismash and rgi with public images?
# RUN bash /deps/install_antismash.sh
# RUN bash /deps/install_rgi.sh $INS_COMMIT
# RUN bash /deps/install_natural_product.sh $INS_COMMIT
RUN micromamba env create -f /deps/env_natural_product.yml


# Set up antibiotic-prediction repo
WORKDIR /antibiotic-prediction
COPY . .

# -----------------------------------------

ENTRYPOINT ["micromamba", "run", "-n", "natural_product" ]

# CMD [ ]
