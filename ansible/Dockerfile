FROM debian:trixie-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ansible-core \
       docker-cli \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Fail the image build immediately if required tools are missing
RUN docker --version && ansible-playbook --version

WORKDIR /automation

COPY deploy.yml .

ENTRYPOINT ["ansible-playbook", "-i", "localhost,", "-c", "local", "deploy.yml"]
