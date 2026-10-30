FROM debian:trixie-slim
RUN apt-get update && apt-get install -y --no-install-recommends ansible-core docker.io ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /automation
COPY deploy.yml .
ENTRYPOINT ["ansible-playbook", "-i", "localhost,", "-c", "local", "deploy.yml"]
