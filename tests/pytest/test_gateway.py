import json
import os
import subprocess
import pytest
BINARY = os.environ['SENSOR_BINARY']
def run(*args):
    return subprocess.run([BINARY, *map(str,args)], capture_output=True, text=True, timeout=5)
@pytest.mark.parametrize('value,state,code', [
    (25,'NORMAL',0),(-40,'NORMAL',0),(79.99,'NORMAL',0),
    (80,'OVERHEAT',0),(125,'OVERHEAT',0),(126,'INVALID',2)])
def test_temperature__critical__boundaries(value,state,code):
    result=run('read',value)
    assert result.returncode == code
    assert json.loads(result.stdout)['state'] == state
@pytest.mark.parametrize('threshold',[-41,126,'invalid'])
def test_configuration__critical__reject_invalid(threshold):
    assert run('read',25,threshold).returncode == 2
def test_configuration__custom_threshold():
    result=run('read',50,40)
    assert result.returncode == 0
    assert json.loads(result.stdout)['state'] == 'OVERHEAT'
@pytest.mark.parametrize('value',['nan','inf','25abc'])
def test_faults__critical__reject_corrupt_input(value):
    assert run('read',value).returncode == 2
def test_release__critical__version_matches():
    result=run('--version')
    assert result.returncode == 0
    assert result.stdout.strip() == os.environ['EXPECTED_VERSION']
