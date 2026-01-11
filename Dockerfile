FROM pytorch/pytorch:2.9.0-cuda12.8-cudnn9-runtime

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /FunASR

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libsndfile1 ffmpeg git \
    && rm -rf /var/lib/apt/lists/*

COPY . /FunASR

RUN cd /FunASR \
    && python -m pip install -e . \
    && python -m pip install -U modelscope huggingface huggingface_hub transformers==4.57.3

