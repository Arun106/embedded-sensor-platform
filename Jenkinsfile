pipeline {
    // Run this job on the Ubuntu node hosting QEMU (127.0.0.1:2222).
    agent any
    options {
        timeout(time: 90, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '15', artifactNumToKeepStr: '5'))
    }
    triggers {
        // Requires the GitHub plugin and a repository webhook to Jenkins.
        githubPush()
    }
    parameters {
        string(name: 'IMAGE_REPOSITORY', defaultValue: 'arunbelursan/embedded-sensor-gateway', description: 'Docker Hub namespace/repository')
        string(name: 'PUSHGATEWAY_URL', defaultValue: 'http://127.0.0.1:9091', description: 'Local Pushgateway reachable from the Jenkins host; override only for another endpoint')
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                dir('reports') { deleteDir() }
                dir('dist') { deleteDir() }
                script {
                    if (!params.IMAGE_REPOSITORY.matches('[a-z0-9][a-z0-9_-]*/[a-z0-9][a-z0-9._-]*')) {
                        error('Set IMAGE_REPOSITORY to your Docker Hub namespace/repository.')
                    }
                    env.IMAGE_REPOSITORY = params.IMAGE_REPOSITORY
                    env.APP_VERSION = "0.1.${env.BUILD_NUMBER}"
                    env.TEST_IMAGE = "embedded-sensor-tests:${env.BUILD_NUMBER}"
                    env.QEMU_TEST_IMAGE = "embedded-sensor-qemu-tests:${env.BUILD_NUMBER}"
                    env.LOCAL_IMAGE = "embedded-sensor-app:${env.BUILD_NUMBER}"
                    env.REMOTE_IMAGE = "${env.IMAGE_REPOSITORY}:${env.APP_VERSION}"
                }
                sh 'mkdir -p reports dist; git rev-parse HEAD > dist/source-revision.txt'
            }
        }
        stage('Build and static analysis') {
            steps {
                sh '''
                    set -eu
                    docker build --target builder --build-arg APP_VERSION="$APP_VERSION" -t "$TEST_IMAGE" .
                '''
            }
        }
        stage('Module tests and release quality gate') {
            steps {
                script {
                    def status = sh(returnStatus: true, script: '''
                        set -eu
                        rm -f reports/ctest.xml reports/pytest.xml reports/robot.xml reports/summary.json reports/metrics.prom reports/triage.json
                        container_id="$(docker create "$TEST_IMAGE" python3 scripts/run_tests.py --version "$APP_VERSION")"
                        cleanup() { docker rm "$container_id" >/dev/null || true; }
                        trap cleanup EXIT
                        test_status=0
                        docker start -a "$container_id" || test_status=$?
                        docker cp "$container_id:/app/reports/." reports/
                        exit "$test_status"
                    ''')
                    // JUnit reports failures honestly; the explicit policy decides release eligibility.
                    junit(testResults: 'reports/ctest.xml,reports/pytest.xml,reports/robot.xml',
                          allowEmptyResults: false, skipMarkingBuildUnstable: true)
                    archiveArtifacts(artifacts: 'reports/**', allowEmptyArchive: false)
                    if (status != 0) error('Test gate failed. Inspect summary.json and triage.json.')
                }
            }
        }
        stage('Build runtime') {
            steps {
                sh '''
                    set -eu
                    docker build --build-arg APP_VERSION="$APP_VERSION" -t "$LOCAL_IMAGE" .
                    docker image save -o dist/image.tar "$LOCAL_IMAGE"
                '''
            }
        }
        stage('Security gate') {
            steps {
                script {
                    try {
                        sh '''
                            set -eu
                            docker run --rm -i --mount type=volume,source=embedded-trivy-cache,target=/root/.cache/trivy \
                              --entrypoint sh aquasec/trivy:0.76.1 -ec '
                                cat > /tmp/image.tar
                                trivy image --input /tmp/image.tar --scanners vuln \
                                  --severity HIGH,CRITICAL --exit-code 1 --format json
                              ' < dist/image.tar > reports/trivy.json
                        '''
                    } finally {
                        archiveArtifacts(artifacts: 'reports/trivy.json', allowEmptyArchive: true)
                    }
                }
            }
        }
        stage('Publish release candidate') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'REGISTRY_USER', passwordVariable: 'REGISTRY_PASSWORD')]) {
                    sh '''
                        set +x
                        set -eu
                        export DOCKER_CONFIG="$(mktemp -d)"
                        cleanup() { rm -rf "$DOCKER_CONFIG"; }
                        trap cleanup EXIT
                        printf '%s' "$REGISTRY_PASSWORD" | docker login --username "$REGISTRY_USER" --password-stdin
                        docker tag "$LOCAL_IMAGE" "$REMOTE_IMAGE"
                        docker push "$REMOTE_IMAGE"
                        docker image inspect --format '{{index .RepoDigests 0}}' "$REMOTE_IMAGE" > dist/release-ref.txt
                        printf '%s\n' "$APP_VERSION" > dist/version.txt
                        cd dist
                        sha256sum image.tar > image.tar.sha256
                    '''
                }
                archiveArtifacts(artifacts: 'dist/*.txt,dist/*.sha256', fingerprint: true)
            }
        }
        stage('Release approval') {
            steps {
                timeout(time: 20, unit: 'MINUTES') {
                    input message: 'Review module tests, security report and candidate digest. Approve Docker checks and QEMU candidate deployment? Activation requires the QEMU test gate.', ok: 'Approve release'
                }
            }
        }
        stage('Deploy with Ansible') {
            steps {
                script {
                    env.RELEASE_REF = readFile('dist/release-ref.txt').trim()
                    if (!env.RELEASE_REF.matches('[a-zA-Z0-9./:_-]+@sha256:[a-f0-9]{64}')) error('Invalid candidate digest.')
                }
                sh 'docker build --network=host --progress=plain -t embedded-sensor-ansible:local ansible/'
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'REGISTRY_USER', passwordVariable: 'REGISTRY_PASSWORD')]) {
                    sh '''
                        set +x
                        set -eu
                        deploy_status=0
                        docker run --rm --mount type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock \
                          -e RELEASE_REF -e EXPECTED_VERSION="$APP_VERSION" -e REGISTRY_USER -e REGISTRY_PASSWORD \
                          embedded-sensor-ansible:local > reports/deployment.log 2>&1 || deploy_status=$?
                        cat reports/deployment.log
                        exit "$deploy_status"
                    '''
                }
            }
        }

        stage('QEMU candidate tests and activation') {
            steps {
                sh 'docker build --network=host --progress=plain --build-arg TEST_IMAGE="$TEST_IMAGE" -f Dockerfile.qemu-tests -t "$QEMU_TEST_IMAGE" .'
                script {
                    def targetStatus = 1
                    try {
                        withCredentials([
                            sshUserPrivateKey(credentialsId: 'qemu-target-ssh', keyFileVariable: 'QEMU_SSH_KEY'),
                            file(credentialsId: 'qemu-known-hosts', variable: 'QEMU_KNOWN_HOSTS')
                        ]) {
                            targetStatus = sh(returnStatus: true, script: 'sh scripts/run_qemu_ci.sh')
                        }
                    } finally {
                        if (fileExists('reports/qemu/pytest.xml')) {
                            junit(testResults: 'reports/qemu/pytest.xml', allowEmptyResults: false, skipMarkingBuildUnstable: true)
                        }
                        if (fileExists('reports/qemu/robot.xml')) {
                            junit(testResults: 'reports/qemu/robot.xml', allowEmptyResults: false, skipMarkingBuildUnstable: true)
                        }
                        archiveArtifacts(artifacts: 'reports/qemu/**,dist/qemu/*.sha256,dist/qemu/artifact/image-ref.txt', allowEmptyArchive: true)
                    }
                    if (targetStatus != 0) error('QEMU deployment, target test gate or activation failed. Inspect reports/qemu/.')
                }
            }
        }
    }
    post {
        always {
            script {
                if (fileExists('reports/metrics.prom') && params.PUSHGATEWAY_URL?.trim()) {
                    withEnv(["METRICS_URL=${params.PUSHGATEWAY_URL.trim()}"]) {
                        warnError('Metrics publication failed') {
                            sh '''
                                set -eu
                                curl --fail --silent --show-error --connect-timeout 5 --max-time 15 \
                                  --request PUT --data-binary @reports/metrics.prom \
                                  "$METRICS_URL/metrics/job/embedded_sensor_pipeline/target/host"
                            '''
                        }
                    }
                }

                if (fileExists('reports/qemu/metrics.prom') && params.PUSHGATEWAY_URL?.trim()) {
                    withEnv(["METRICS_URL=${params.PUSHGATEWAY_URL.trim()}"]) {
                        warnError('QEMU metrics publication failed') {
                            sh '''
                                set -eu
                                curl --fail --silent --show-error --connect-timeout 5 --max-time 15 \
                                  --request PUT --data-binary @reports/qemu/metrics.prom \
                                  "$METRICS_URL/metrics/job/embedded_sensor_pipeline/target/qemu"
                            '''
                        }
                    }
                }
                archiveArtifacts(artifacts: 'reports/**', allowEmptyArchive: true)
                sh 'rm -f dist/image.tar'
            }
        }
    }
}
