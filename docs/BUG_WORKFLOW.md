# Test failure versus confirmed bug
reports/triage.json records failed tests with stable identifiers. A failed test is NOT automatically a confirmed product bug.
Investigate application defect, flaky test, bad expectation, or infrastructure failure first.
For this starter, bugs/bugs.json is a reviewed local tracker, not an Azure Boards integration.
Only confirmed records contribute to tracked-bug dashboard panels. Start with []: no synthetic bugs are seeded.
Example record (replace values with actual evidence):
```json
{"id":"BUG-001","module":"temperature_input","state":"open","test_id":"stable identifier from triage.json","description":"Observed behavior","fix_commit":null,"verified_build":null}
```
Use states open, resolved, closed. Resolved requires fix_commit. Closed additionally requires verified_build and review of the regression evidence.
Do not mark bugs fixed because an unrelated rerun passed. Keep fixed-test evidence and issue links in release notes.
Next increment replaces this file with read-only export from Azure Boards/Jira plus deduplicated issue creation after triage.
