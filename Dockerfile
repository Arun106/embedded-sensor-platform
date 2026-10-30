FROM debian:trixie-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends g++ cmake ninja-build cppcheck python3 python3-venv ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements-test.txt .
RUN python3 -m venv /opt/testenv && /opt/testenv/bin/pip install --no-cache-dir -r requirements-test.txt
ENV PATH="/opt/testenv/bin:${PATH}"
COPY . .
ARG APP_VERSION=0.1.0
RUN cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DAPP_VERSION=${APP_VERSION} && cmake --build build --parallel 2
RUN python3 -m unittest discover -s tests/policy -v
RUN cppcheck --enable=warning,performance,portability --error-exitcode=1 --std=c++17 --suppress=missingIncludeSystem -Iapp app
FROM gcr.io/distroless/cc-debian13:nonroot AS runtime
COPY --from=builder /app/build/sensor-gateway /usr/local/bin/sensor-gateway
ENTRYPOINT ["/usr/local/bin/sensor-gateway"]
CMD ["read", "25"]
