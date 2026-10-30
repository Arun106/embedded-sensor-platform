# Monitoring integration
Reuse your existing Grafana and Prometheus. Do not run a second Grafana on port 3000.
Start one service-level batch metrics gateway on the same Ubuntu Docker host:
```bash
docker run -d --name embedded-pushgateway --restart unless-stopped --network host prom/pushgateway:latest --web.listen-address=127.0.0.1:9091
```
The gateway's latest snapshot is transient across container removal/restart; the next pipeline run republishes it. Archived reports remain the evidence of record.
Add this job to the EXISTING Prometheus configuration's scrape_configs list:
```yaml
  - job_name: embedded-test-results
    honor_labels: true
    static_configs:
      - targets: ['127.0.0.1:9091']
```
Your Prometheus uses host networking. If its config was COPY-ed into its image, changing a host file alone does not update the running container: rebuild that monitoring image and recreate only that container, preserving its named data volume and original run options.
Import module-dashboard.json into Grafana and choose your existing Prometheus datasource.
The gateway stores the latest full-suite result, not an immutable record of every build. Do not use build number, commit or test-case ID as metric labels.
Freshness: time() - embedded_test_last_run_timestamp_seconds.
If the pipeline fails before tests produce a new report, the last snapshot stays; inspect its age and use Jenkins' own build metrics for pipeline health.
Test-gate success is not deployment success. The deployment log and Jenkins stage remain separate evidence.
Bug panels currently read the reviewed bugs/bugs.json file; automatic Azure Boards synchronization is a later integration.
