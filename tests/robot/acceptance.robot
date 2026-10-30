*** Settings ***
Library    Process
Library    OperatingSystem

*** Variables ***
${BINARY}    %{SENSOR_BINARY}
${EXPECTED_VERSION}    %{EXPECTED_VERSION}

*** Test Cases ***
temperature__normal_reading
    ${result}=    Run Process    ${BINARY}    read    25    timeout=5s
    Should Be Equal As Integers    ${result.rc}    0
    Should Contain    ${result.stdout}    NORMAL

configuration__critical__custom_threshold
    ${result}=    Run Process    ${BINARY}    read    50    40    timeout=5s
    Should Be Equal As Integers    ${result.rc}    0
    Should Contain    ${result.stdout}    OVERHEAT

faults__critical__invalid_reading
    ${result}=    Run Process    ${BINARY}    read    150    timeout=5s
    Should Be Equal As Integers    ${result.rc}    2

release__critical__approved_version
    ${result}=    Run Process    ${BINARY}    --version    timeout=5s
    Should Be Equal As Integers    ${result.rc}    0
    Should Be Equal    ${result.stdout}    ${EXPECTED_VERSION}
