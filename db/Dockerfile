FROM postgres:latest

ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG POSTGRES_DB

USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    postgresql-server-dev-all \
    && rm -rf /var/lib/apt/lists/*

RUN cd /tmp \
    && git clone --branch v0.5.0 https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make \
    && make install