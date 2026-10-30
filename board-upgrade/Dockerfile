FROM debian:trixie-slim
RUN apt-get update && apt-get install -y --no-install-recommends ansible-core python3 ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /work
COPY . .
RUN python3 -m unittest discover -s tests -v && ansible-playbook -i localhost, ansible/upgrade.yml --syntax-check
RUN cp config/board.json board.json && mkdir -p reports
CMD ["ansible-playbook", "-i", "localhost,", "ansible/upgrade.yml"]
