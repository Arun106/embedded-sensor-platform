# Simulated board upgrade with Ansible

This is a teaching simulation, not FPGA flashing, QEMU, or hardware validation.
The board is a JSON file. Ansible validates its revision and bootloader,
calculates the allowed update path, applies one simulated update at a time,
reads back state after every step, and saves before/after evidence.

Files:
- `config/release.json`: example compatibility rules and target version.
- `config/board.json`: initial mock board, copied into each fresh container.
- `ansible/upgrade.yml`: prechecks, path selection, final verification and reporting.
- `ansible/step.yml`: update and readback for one step.
- `board.py`: simulated board adapter; no device access or flashing commands.
- `tests/test_upgrade.py`: bridge, direct, rerun, rejection and invalid-policy cases.

Run from the repository root with Jenkins idle and sufficient free disk space:

```sh
docker build -t embedded-board-simulation:local board-upgrade/
docker run --rm embedded-board-simulation:local
```

The new Jenkins stage runs before runtime image creation and blocks publishing
if the simulation fails. Existing reports archival includes its log and JSON.
Default path: firmware 1 -> bridge 2 -> target 3. An unknown starting version,
wrong revision or wrong bootloader stops before changing simulated firmware.
Each fresh container resets the fixture. Rerunning the playbook inside the same
container at firmware 3 performs no further simulated firmware updates.

To run policy tests locally:
```sh
cd board-upgrade
python3 -m unittest discover -s tests -v
```

Before replacing this with a hardware workflow, obtain the actual board model,
vendor tools, readback protocol, documented update matrix and release artifacts.
Add bench locking, artifact authenticity/integrity checks, power/reconnect and
health checks, failure evidence and the vendor-approved recovery procedure.
Do not treat updating a JSON value as proof of reboot, flashing or hardware health.
Real hardware updates must run on an exclusively reserved bench and must not be
parallelized. The current Jenkins disableConcurrentBuilds covers this one job
only; it is not a lock shared across independent jobs.

Validation here: five Python policy tests pass. Docker/Ansible execution must be
validated by running the new stage; the editing environment has no Docker daemon.
