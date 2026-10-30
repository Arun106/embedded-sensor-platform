# QEMU test monitoring with existing Prometheus and Grafana

## Architecture

Jenkins runs build tests and QEMU tests. Each gate writes metrics.prom. Jenkins PUTs these latest batch snapshots to Pushgateway. Prometheus scrapes Pushgateway. Grafana queries Prometheus. Jenkins XML/HTML artifacts remain detailed evidence; Prometheus is not the test-case database.

The application is a short-lived CLI, so a batch-result gateway is appropriate here. This does not instrument a continuously running sensor service or emulate physical sensors.

## 1. Start Pushgateway only if absent

On the Ubuntu host (arun@ubuntu), check first:

    docker ps -a --filter name=embedded-pushgateway

If no such container exists:

    docker run -d --name embedded-pushgateway --restart unless-stopped --network host prom/pushgateway:latest --web.listen-address=127.0.0.1:9091

If it exists but is stopped:

    docker start embedded-pushgateway

Check its metrics endpoint:

    curl --fail http://127.0.0.1:9091/metrics

The image tag latest is retained for this local lab setup; pin an approved release/digest when stabilizing the infrastructure. No second Prometheus/Grafana container is required. Gateway metrics in this command are not persistent across container removal/restart; the next pipeline execution republishes them.

## 2. Configure the existing Prometheus

Merge this entry under the existing scrape_configs list. Do not replace your Jenkins scrape job:

    - job_name: embedded-test-results
      honor_labels: true
      static_configs:
        - targets: ['127.0.0.1:9091']

This assumes your existing embedded-prometheus container uses host networking, as in the current lab setup. You can confirm:

    docker inspect embedded-prometheus --format '{{.HostConfig.NetworkMode}}'

If it is not host, 127.0.0.1 inside it refers to the container, so adapt the gateway network/address first.

Find how its configuration is supplied:

    docker inspect embedded-prometheus --format '{{json .Mounts}}'
    docker inspect embedded-prometheus --format '{{json .Config.Cmd}}'

For a bind-mounted config, edit its host source and restart the existing container to reload. For a config copied into embedded-prometheus:local at image build time, rebuild/recreate that service with its original run options and data volume. A restart alone will not incorporate changes to an unrelated host file. Do not delete volumes. Preserve your current Prometheus scrape jobs and data.

## 3. Enable pipeline publishing

In Jenkins Build with Parameters:

    PUSHGATEWAY_URL=http://127.0.0.1:9091

Jenkins publishes build metrics to `/metrics/job/embedded_sensor_pipeline/target/host` and QEMU metrics to `/metrics/job/embedded_sensor_pipeline/target/qemu`. Distinct groups avoid overwriting each other.

## 4. Import the dashboard

Grafana -> Dashboards -> New -> Import -> upload monitoring/qemu-dashboard.json. Choose your existing Prometheus data source and import. UI labels can differ slightly by Grafana version.

The dashboard shows Build and QEMU columns with:

- Overall test pass rate.
- Test gate status.
- Age of the last test result.
- Module pass rates.
- Module passed/failed/error/skipped counts.
- Reviewed bug counts per module and open/resolved/closed state.

Example query in Explore:

    embedded_module_pass_rate_percent{job="embedded_sensor_pipeline",target="qemu"}

Expected module labels: temperature_input, threshold_control, cooling_output, fault_diagnostics, firmware_identity. See MODULE-ARCHITECTURE.md for the updated dashboard imports.

Freshness query:

    time() - embedded_test_last_run_timestamp_seconds{job="embedded_sensor_pipeline",target="qemu"}

With honor_labels: true, the pushed job label remains embedded_sensor_pipeline. Without it, the exported_job/job labels differ and the supplied dashboard queries will not match.

## Interpretation

A previous successful target snapshot can remain if a later build fails before target tests run. Always inspect result age, pipeline status and deployment/activation logs. The test-gate metric is not a live application-health or deployment-success metric. Deliberately failed tests remain in XML/triage reports. Only reviewed bugs in bugs/bugs.json count as confirmed tracked bugs; no automatic issue creation or fix detection is implemented.
