# Built by Flappeh <bonar_david@rocketmail.com>

ARG FUNCTION_DIR="/bot"

FROM python:3.11-slim-bullseye as build-stage

ARG FUNCTION_DIR

# Install build deps

# RUN apt-get update && \
#   apt-get install -y \
#   g++ \
#   make \
#   cmake \
#   unzip \
#   libcurl4-openssl-dev

# RUN apt-get install -y --fix-missing \
#     build-essential \
#     cmake \
#     gfortran \
#     git \
#     wget \
#     curl \
#     ffmpeg \
#     libsm6 \
#     libxext6 \
#     graphicsmagick \
#     libgraphicsmagick1-dev \
#     libatlas-base-dev \
#     libavcodec-dev \
#     libavformat-dev \
#     libgtk2.0-dev \
#     libjpeg-dev \
#     liblapack-dev \
#     libswscale-dev \
#     pkg-config \
#     python3-dev \
#     python3-numpy \
#     software-properties-common \
#     zip \
#     && apt-get clean && rm -rf /tmp/* /var/tmp/*

RUN mkdir -p ${FUNCTION_DIR}
COPY . ${FUNCTION_DIR}

WORKDIR ${FUNCTION_DIR}

RUN pip install --upgrade pip

RUN pip install -r requirements.txt --target ${FUNCTION_DIR}

# Runtime stage
FROM python:3.11-slim-bullseye as runtime-stage

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}


COPY --from=build-stage ${FUNCTION_DIR} ${FUNCTION_DIR}

COPY . ${FUNCTION_DIR}

ARG FUNCTION_DIR

# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}


CMD ["python", "main.py"]