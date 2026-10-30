import json

from test_target import run_target as _run_target


def verify_reading(value, expected_state, threshold=None):
    arguments = ["read", value]
    if threshold is not None:
        arguments.append(threshold)

    result = _run_target(*arguments)
    assert result.returncode == 0, (
        f"exit={result.returncode}; stderr={result.stderr}"
    )
    data = json.loads(result.stdout)
    assert data["state"] == expected_state, data
    assert data["value"] == float(value), data
    expected_threshold = 80 if threshold is None else float(threshold)
    assert data["threshold"] == expected_threshold, data


def verify_invalid_threshold(threshold):
    result = _run_target("read", 25, threshold)
    assert result.returncode == 2, (
        f"exit={result.returncode}; stderr={result.stderr}"
    )


def verify_invalid_reading(value):
    result = _run_target("read", value)
    assert result.returncode == 2, (
        f"exit={result.returncode}; stderr={result.stderr}"
    )
    assert json.loads(result.stdout)["state"] == "INVALID"


def verify_release(expected_version):
    result = _run_target("--version")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == expected_version, result.stdout
