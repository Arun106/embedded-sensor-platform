#!/usr/bin/env python3
"""Synthetic alert exercise; never replaces host or QEMU test evidence."""
import argparse
import time
import urllib.request

MODULES = ['temperature_input', 'threshold_control', 'cooling_output',
           'fault_diagnostics', 'firmware_identity']

def metrics(rate):
    failures = {100: [0, 0, 0, 0, 0], 96: [1, 1, 2, 0, 0],
                93: [2, 2, 3, 0, 0]}[rate]
    lines = [f'embedded_test_pass_rate_percent {rate}',
             f'embedded_test_last_run_timestamp_seconds {int(time.time())}',
             'embedded_test_gate_passed 1']
    for module, failed in zip(MODULES, failures):
        for status, count in [('passed', 20-failed), ('failed', failed),
                              ('error', 0), ('skipped', 0)]:
            lines.append(f'embedded_test_cases{{module="{module}",status="{status}"}} {count}')
        lines.append(f'embedded_module_pass_rate_percent{{module="{module}"}} {(20-failed)*5}')
    return '\n'.join(lines)+'\n'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rate', type=int, choices=[100, 96, 93])
    parser.add_argument('--url', default='http://127.0.0.1:9091')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    payload = metrics(args.rate)
    if args.dry_run:
        print(payload, end='')
    else:
        request = urllib.request.Request(args.url.rstrip('/') +
            '/metrics/job/embedded_sensor_pipeline/target/qemu-simulation',
            data=payload.encode(), method='PUT',
            headers={'Content-Type': 'text/plain; version=0.0.4'})
        with urllib.request.urlopen(request, timeout=15):
            print(f'SYNTHETIC: {args.rate}/100 passed; no real test results changed.')
