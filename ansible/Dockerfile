FROM debian:trixie-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ansible-core docker-cli openssh-client ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN docker --version && ansible-playbook --version && ssh -V
WORKDIR /automation
COPY deploy.yml .
ENTRYPOINT ["ansible-playbook", "-i", "localhost,", "-c", "local", "deploy.yml"]
