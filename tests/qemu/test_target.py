"""Run the release candidate through SSH; connection settings come from CI."""
import json
import os
import shlex
import subprocess
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]

def run_target(*args):
    binary = os.environ.get('QEMU_BINARY', '/usr/local/bin/sensor-gateway')
    command = shlex.join([binary, *map(str, args)])
    return subprocess.run([
        'ssh', '-i', os.environ.get('QEMU_SSH_KEY', str(ROOT / '.qemu/sensor-lab-key')),
        '-p', os.environ.get('QEMU_PORT', '2222'),
        '-o', 'BatchMode=yes', '-o', 'IdentitiesOnly=yes',
        '-o', 'StrictHostKeyChecking=yes',
        '-o', 'UserKnownHostsFile=' + os.environ.get('QEMU_KNOWN_HOSTS', str(ROOT / '.qemu/known_hosts')),
        '-o', 'ConnectTimeout=120',
        '-o', 'ServerAliveInterval=15', '-o', 'ServerAliveCountMax=3',
        os.environ.get('QEMU_USER', 'sensor') + '@' + os.environ.get('QEMU_HOST', '127.0.0.1'),
        command,
    ], capture_output=True, text=True, timeout=150)

def response(result):
    assert result.returncode == 0, (
        f'exit={result.returncode}, stdout={result.stdout!r}, stderr={result.stderr!r}'
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail(f'Expected JSON, received {result.stdout!r}')

def test_release__critical__deployed_version():
    result = run_target('--version')
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == os.environ.get('EXPECTED_VERSION', '0.1.5')

@pytest.mark.parametrize('value,expected', [
    (-40, 'NORMAL'), (25, 'NORMAL'), (79.99, 'NORMAL'),
    (80, 'OVERHEAT'), (80.01, 'OVERHEAT'),
])
def test_temperature__critical__default_threshold(value, expected):
    data = response(run_target('read', value))
    assert data['state'] == expected
    assert data['value'] == pytest.approx(value)
    assert data['threshold'] == pytest.approx(80)

@pytest.mark.parametrize('threshold,expected', [(20, 'OVERHEAT'), (30, 'NORMAL')])
def test_configuration__custom_threshold(threshold, expected):
    data = response(run_target('read', 25, threshold))
    assert data['state'] == expected
    assert data['value'] == pytest.approx(25)
    assert data['threshold'] == pytest.approx(threshold)

@pytest.mark.parametrize('threshold', [-41, 126, 'invalid'])
def test_configuration__critical__invalid_threshold(threshold):
    result = run_target('read', 25, threshold)
    assert result.returncode == 2, f'exit={result.returncode}; stderr={result.stderr}'
