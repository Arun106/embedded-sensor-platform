# Thermal controller verification architecture

This is a software thermal-control demonstrator with host tests and a QEMU virtual target. A physical HiL bench would add sensor signal generation, electrical I/O, an ECU and actuator/load feedback. Those interfaces are not implemented here.

| Module label | Meaning and actual evidence |
| --- | --- |
| temperature_input | Temperature values, range boundaries and reading response |
| threshold_control | Configurable overheat threshold and invalid configuration rejection |
| cooling_output | Software cooling request: NORMAL means no request; OVERHEAT means request. No fan, relay, PWM or GPIO is driven. |
| fault_diagnostics | Corrupt, nonfinite and out-of-range input rejection |
| firmware_identity | Expected release version reported by the candidate binary |

Application implementation: app/thermal_control.hpp and app/main.cpp.
Test adapters: tests/pytest/test_thermal_controller.py and tests/qemu/test_thermal_target.py, plus Robot acceptance suites.
Gate reads module prefixes from config/test-policy.json or config/qemu-test-policy.json. Module names flow through XML, summary, triage, metrics and reviewed bug labels.

## Two dashboards with distinct purposes

- Thermal Controller — Module Verification: choose Host build, QEMU target or Alert simulation. One overall result and named module bars for the selected source.
- Thermal Controller — Host Build vs QEMU: compare build verification on the left with virtual-target verification on the right. Synthetic results are excluded.

Existing dashboard UIDs are preserved so imports overwrite the previous dashboards instead of creating additional copies. Existing installed dashboards are not changed by git pull alone.

100% means every reported case passed in the latest snapshot. It is not a claim of perfect software, full requirement coverage or hardware health. Overall pass rate uses test counts, not an average of module percentages. A test gate passing does not mean activation/deployment succeeded.

## Apply on Ubuntu

1. From ~/repos/embedded-sensor-platform run git pull --ff-only. Commit or stash any local edits first if Git reports a conflict; do not discard them.
2. Run Jenkins using a NEW, unused release version if publishing, with PUSHGATEWAY_URL=http://127.0.0.1:9091. Complete QEMU verification to publish new target results. Host results now use target="host"; QEMU results keep target="qemu".
3. In Grafana, import monitoring/module-dashboard.json and monitoring/qemu-dashboard.json. Select the existing Prometheus data source and confirm overwrite for each existing UID.
4. Refresh after a scrape interval. Select QEMU target in Module Verification. Current module charts filter out historical old module labels. Old Prometheus history remains intact.

For alert exercises use python3 monitoring/push-simulation.py 96, then 93, then 96 for recovery. The synthetic snapshot always uses target="qemu-simulation" and contains 100 synthetic cases. Each of five modules has 20 cases. These numbers are not QEMU test results or reviewed bugs.

The existing simulation alert can remain loaded: its name, metric and target selector are compatible. To update its wording, copy monitoring/simulation-alerts.yml into the already referenced /etc/prometheus/simulation-alerts.yml, validate with promtool and send HUP. If no rule reference is loaded, add it to your existing Prometheus rule_files list first. Preserve existing rules and scrape jobs. Alert delivery requires Alertmanager; a firing Prometheus rule alone does not send email.

## Inventory and validation

Host suite: 21 reported cases (1 CTest, 16 pytest, 4 Robot).
QEMU suite: 19 reported cases (13 pytest, 6 Robot).
The extra two cases at each layer verify the logical cooling output using the existing state response. No new physical interface or application output field is introduced.
Release policy remains strictly above 90%, all critical tests passing, complete framework/module reports and no execution errors.
The historical evidence/host-test-summary.json is preserved as an old result, not renamed to imply those tests had run under the new labels.
