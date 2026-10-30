# Embedded Sensor Platform

A small C++17 thermal-controller demonstrator with automated testing, release
gates, virtual-target verification, deployment playbooks, and Grafana metrics.

The application is a one-shot command. It models a cooling request only; it
does not connect to physical sensors or actuators.

## What is included

- CMake and CTest build for the C++ application.
- Pytest and Robot Framework acceptance tests.
- QEMU-oriented virtual-target tests and policy.
- A release gate that checks test coverage, critical tests, and report files.
- Jenkins, Docker, Ansible, and Grafana configuration for the delivery flow.

## Project layout

| Folder | Purpose |
| --- | --- |
| `app/` | Thermal-controller source code and C++ unit tests. |
| `tests/` | Pytest, Robot Framework, release-policy, and QEMU tests. |
| `scripts/` | Full test runner and release-gate tools. |
| `config/` | Test policy and release metadata. |
| `ansible/` | Deployment and QEMU activation playbooks. |
| `monitoring/` | Grafana dashboards and metrics configuration. |
| `docs/` | Operational notes, milestones, and bug workflow. |

## Quick start

Requirements: CMake, a C++17 compiler, Ninja, Python 3, and `venv` support.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-test.txt

cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DAPP_VERSION=0.1.0-local
cmake --build build --parallel 2
python scripts/run_tests.py --version 0.1.0-local
```

Test reports are written to `reports/`. Check `reports/summary.json` after a
full run.

## Run individual test suites

```bash
ctest --test-dir build --output-on-failure
python -m pytest tests/pytest -q
python -m robot --outputdir reports/robot --xunit reports/robot.xml tests/robot
```

## Release gate

The release policy requires:

- More than 90% of all reported tests to pass.
- Every critical test to pass.
- No execution errors and all expected reports to be present.
- At least 21 host cases, or 19 QEMU cases.

Exactly 90% does not pass. See `config/test-policy.json` for the host policy
and `config/qemu-test-policy.json` for the virtual-target policy.

## Delivery and monitoring

The Jenkins pipeline builds a candidate image, runs the release gate, waits for
manual approval, and deploys the approved image digest through Ansible.

Before using the pipeline, set your own Docker Hub image namespace and create
the `dockerhub-creds` Jenkins credential. Never commit tokens or passwords.

### Trigger Jenkins from GitHub

The pipeline uses the GitHub push trigger. In Jenkins, create a **Pipeline from
SCM** job that points to this repository and uses `Jenkinsfile`. Then add a
GitHub webhook at:

```text
https://<your-jenkins-host>/github-webhook/
```

Select the **Pushes** event. A push to the configured branch will then start a
new build. Jenkins must be reachable from GitHub; use a secure public endpoint
or a GitHub App/integration appropriate for your environment.

For metrics and dashboards, start with [monitoring/START.md](monitoring/START.md)
and [monitoring/MODULE-ARCHITECTURE.md](monitoring/MODULE-ARCHITECTURE.md).

## Current scope

QEMU validation is virtual-target verification, not physical hardware testing.
Physical sensor/actuator I/O, Yocto integration, and external issue-tracker
synchronization are future work.

For contributor commands and conventions, see [AGENTS.md](AGENTS.md).
