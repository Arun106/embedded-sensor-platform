# Embedded Sensor Platform — Jenkins increment 1

A small original C++ application with CMake, CTest, pytest, Robot Framework, an explicit release policy, Docker Hub candidate publication, manual approval, Ansible release execution, and Grafana module metrics.

## Honest scope
- This increment is a HOST/container pipeline. It does NOT boot QEMU, flash firmware, implement a Yocto layer, or constitute physical HiL.
- The application is a one-shot command, not a persistent telemetry service.
- Confirmed bugs are tracked in reviewed bugs/bugs.json for now. Failure triage is automatic; Azure Boards/Jira synchronization is NOT implemented.
- Jenkins orchestration, container builds, registry push/pull, Ansible execution and Grafana import need verification on your machine. Host compilation and all test suites were exercised during preparation; see VALIDATION.md.

## Modules and tests
- temperature: boundaries and normal readings
- configuration: valid/custom thresholds and rejected configuration
- faults: malformed, non-finite and out-of-range input
- release: exact expected version
19 reported test cases: 1 CTest case (several C++ assertions), 14 pytest cases, 4 Robot cases.
Suites overlap intentionally to demonstrate different test layers; pass rate is an unweighted case count, not a safety measure or coverage score.

## Release policy
Full-suite rate = passed / all reported cases * 100. Skips remain in the denominator.
Require strictly >90%, every critical test passed, no execution errors, all reports/frameworks and all modules present, and at least 19 cases.
Exactly 90% fails. For this 19-case suite one noncritical failure can be accepted (18/19=94.74%); any critical failure blocks release regardless of rate.
An authorized reviewer must still approve release. Decide real production criteria with the team.
Missing reports and malformed XML block the gate. Update config/test-policy.json through review as the test inventory changes.
Jenkins JUnit deliberately does not set UNSTABLE automatically: the explicit gate decides eligibility. Failed tests stay visible in test reports and triage.
The runtime image security gate separately rejects HIGH/CRITICAL findings; the test percentage cannot override it.

## Local first run (Ubuntu)
```bash
sudo apt update
sudo apt install -y build-essential cmake ninja-build python3-venv
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-test.txt
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DAPP_VERSION=0.1.0-local
cmake --build build --parallel 2
python scripts/run_tests.py --version 0.1.0-local
cat reports/summary.json
```
Docker alternative (no host tool installation):
```bash
docker build --target builder --build-arg APP_VERSION=0.1.0-local -t embedded-sensor-tests:local .
docker create --name sensor-tests-local embedded-sensor-tests:local python3 scripts/run_tests.py --version 0.1.0-local
docker start -a sensor-tests-local
mkdir -p reports
docker cp sensor-tests-local:/app/reports/. reports/
docker rm sensor-tests-local
```
Use a unique container name if an earlier test container still exists. Preserve the test exit status in automation; Jenkinsfile does so.

## Jenkins setup
1. Put this project in YOUR own Git repository (not ttroy50/cmake-examples).
2. Create a Pipeline from SCM using that repo and Script Path Jenkinsfile. Agent needs Linux, Git, Docker and curl; no CMake or Ansible host installation is required.
3. Create a Docker Hub repository embedded-sensor-gateway.
4. Jenkins Credentials: username/password type, ID dockerhub-creds; username Docker Hub ID; password scoped access token. Never put it in Git.
5. Set IMAGE_REPOSITORY to your namespace/embedded-sensor-gateway. Leave PUSHGATEWAY_URL empty until monitoring is configured. Pipeline parameters may appear after the first run; the placeholder intentionally fails validation rather than pushing elsewhere.
6. Review the reports, approve the input step and check Ansible output. Manual input is a lab approval; production governance should restrict approvers and protect Jenkinsfile changes.
7. Registry digest selects the exact published candidate. Ansible authenticates in an ephemeral runner, pulls that digest, verifies version and executes a sensor smoke test. Docker socket access is host-admin-equivalent; run only trusted pipeline code.

## Registry portability
Docker Hub initially. JFrog Artifactory/other OCI registries can replace it by changing registry endpoint, image path, credentials and login command.
Current Jenkinsfile intentionally validates a Docker Hub namespace/repository; adapt that validation when adding a private hostname/path.
Artifactory's Docker repository is itself a registry. Generic firmware packages and reports use appropriate generic repositories; they are not automatically container images.
Publish immutable candidate versions and promote the same digest after approval. Do not rebuild during CD.

## Observability
Follow monitoring/START.md. Import monitoring/module-dashboard.json. Module metrics come from actual XML reports; no fabricated outcomes.
Jenkins metrics still provide whole-pipeline build outcomes. For bugs, read docs/BUG_WORKFLOW.md.

## Next increments
1. Persistent application service and separate post-deployment suites.
2. Yocto image and package recipe, package ptest if required, QEMU boot, SSH adapter and target acceptance tests.
3. External issue tracker synchronization; verified fix history.
4. Target-health and deployment metrics in addition to test metrics.
5. Reviewed module impact selection for PRs; keep full-suite release qualification.
Dependencies use bounded versions and base tags for this starter. Lock package versions and image digests after validating your environment.
