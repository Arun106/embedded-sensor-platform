# Embedded Sensor Platform contributor guide

## Overview

This repository contains a C++17 thermal-controller demonstrator (`app/`) and
its CI/CD, virtual-target, deployment, and monitoring configuration. The host
application is a one-shot command; it does not control physical I/O.

## Repository layout

- `app/`: application sources and C++ unit-test executable.
- `tests/`: pytest, Robot Framework, QEMU, and policy tests.
- `scripts/`: test orchestration and release-gate tooling.
- `config/`: host/QEMU release policy and release metadata.
- `ansible/`, `monitoring/`, and `docs/`: deployment, observability, and
  operational documentation.

## Build and test

Use an out-of-source CMake build. A local development run is:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-test.txt
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DAPP_VERSION=0.1.0-local
cmake --build build --parallel 2
python scripts/run_tests.py --version 0.1.0-local
```

Run a focused host suite with:

```bash
ctest --test-dir build --output-on-failure
python -m pytest tests/pytest -q
python -m robot --outputdir reports/robot --xunit reports/robot.xml tests/robot
```

The release gate consumes reports in `reports/`; use `scripts/run_tests.py`
when validating a complete change. QEMU tests have separate scripts and policy
under `tests/qemu/` and `config/qemu-test-policy.json`.

## Code conventions

- Keep C++ compatible with C++17 and compile cleanly under `-Wall -Wextra
  -Wpedantic -Werror`.
- Preserve the module names documented in `README.md` and
  `monitoring/MODULE-ARCHITECTURE.md`; reporting and release policy depend on
  them.
- Update tests and release-policy fixtures when changing reported test
  inventory, module attribution, or criticality.
- Do not put credentials, registry tokens, or deployment secrets in the
  repository.

## Before handing off

- Run the narrowest relevant tests, then the full host suite for behavior or
  policy changes.
- Inspect `reports/summary.json` and gate output after a full suite.
- Keep generated build and report artifacts out of commits unless explicitly
  requested.
