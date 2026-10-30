#!/bin/sh
# Runs on the Jenkins Ubuntu agent. No workspace bind mounts are used.
set -eu
set +x
: "${APP_VERSION:?APP_VERSION is required}"
: "${QEMU_SSH_KEY:?Jenkins SSH credential is required}"
: "${QEMU_KNOWN_HOSTS:?Jenkins known-hosts credential is required}"
: "${QEMU_TEST_IMAGE:?QEMU test image is required}"
mkdir -p reports/qemu dist/qemu/artifact
automation_id=''
extract_id=''
test_id=''
cleanup() {
    for container_id in "$test_id" "$extract_id" "$automation_id"; do
        if [ -n "$container_id" ]; then
            docker rm -f "$container_id" >/dev/null 2>&1 || true
        fi
    done
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
release_ref=$(cat dist/release-ref.txt)
extract_id=$(docker create "$release_ref")
docker cp "$extract_id:/usr/local/bin/sensor-gateway" dist/qemu/artifact/sensor-gateway
docker rm "$extract_id" >/dev/null
extract_id=''
printf '%s\n' "$release_ref" > dist/qemu/artifact/image-ref.txt
sha256sum dist/qemu/artifact/sensor-gateway > dist/qemu/binary.sha256

automation_id=$(docker create --network host -e EXPECTED_VERSION="$APP_VERSION" \
    --entrypoint sleep embedded-sensor-ansible:local infinity)
docker cp ansible/inventory-qemu.yml "$automation_id:/automation/inventory.yml"
docker cp ansible/deploy-qemu.yml "$automation_id:/automation/deploy-qemu.yml"
docker cp ansible/activate-qemu.yml "$automation_id:/automation/activate-qemu.yml"
docker cp "$QEMU_SSH_KEY" "$automation_id:/automation/sensor-lab-key"
docker cp "$QEMU_KNOWN_HOSTS" "$automation_id:/automation/known_hosts"
docker cp dist/qemu/artifact "$automation_id:/automation/artifact"
docker start "$automation_id" >/dev/null
docker exec "$automation_id" chmod 600 /automation/sensor-lab-key

deploy_status=0
docker exec "$automation_id" ansible-playbook -i /automation/inventory.yml \
    /automation/deploy-qemu.yml -T 120 > reports/qemu/deployment.log 2>&1 || deploy_status=$?
cat reports/qemu/deployment.log
if [ "$deploy_status" -ne 0 ]; then exit "$deploy_status"; fi

test_id=$(docker create --network host \
    -e EXPECTED_VERSION="$APP_VERSION" \
    -e QEMU_BINARY="/opt/sensor-gateway/releases/$APP_VERSION/sensor-gateway" \
    -e QEMU_SSH_KEY=/run/sensor-lab-key -e QEMU_KNOWN_HOSTS=/run/known_hosts \
    --entrypoint sh "$QEMU_TEST_IMAGE" -ec '
        chmod 600 /run/sensor-lab-key
        mkdir -p reports/qemu
        set +e
        python3 -m pytest tests/qemu/test_target.py -v --junitxml=reports/qemu/pytest.xml
        pytest_status=$?
        python3 -m robot --pythonpath tests/qemu --outputdir reports/qemu \
            --xunit robot.xml tests/qemu/acceptance.robot
        robot_status=$?
        python3 scripts/gate.py --reports reports/qemu --policy config/qemu-test-policy.json --bugs bugs/bugs.json
        gate_status=$?
        # Framework startup errors must never qualify for a percentage waiver.
        if [ "$pytest_status" -gt 1 ] || [ "$robot_status" -ge 250 ]; then exit 2; fi
        exit "$gate_status"
    ')
docker cp "$QEMU_SSH_KEY" "$test_id:/run/sensor-lab-key"
docker cp "$QEMU_KNOWN_HOSTS" "$test_id:/run/known_hosts"
test_status=0
docker start -a "$test_id" > reports/qemu/test-console.log 2>&1 || test_status=$?
cat reports/qemu/test-console.log
copy_status=0
docker cp "$test_id:/app/reports/qemu/." reports/qemu/ || copy_status=$?
if [ "$copy_status" -ne 0 ]; then exit "$copy_status"; fi
if [ "$test_status" -ne 0 ]; then
    echo 'QEMU gate failed. Active application was not changed.'
    exit "$test_status"
fi

activation_status=0
docker exec "$automation_id" ansible-playbook -i /automation/inventory.yml \
    /automation/activate-qemu.yml -T 120 > reports/qemu/activation.log 2>&1 || activation_status=$?
cat reports/qemu/activation.log
exit "$activation_status"
