*** Settings ***
Library    target_keywords.py

*** Variables ***
${EXPECTED_VERSION}    %{EXPECTED_VERSION=0.1.5}

*** Test Cases ***
temperature__normal_reading
    [Tags]    temperature
    Verify Reading    25    NORMAL

temperature__critical__overheat_boundary
    [Tags]    temperature    critical
    Verify Reading    80    OVERHEAT

configuration__critical__custom_threshold
    [Tags]    configuration    critical
    Verify Reading    25    OVERHEAT    20

configuration__critical__invalid_threshold
    [Tags]    configuration    critical
    Verify Invalid Threshold    126

faults__critical__out_of_range_reading
    [Tags]    faults    critical
    Verify Invalid Reading    -41

release__critical__expected_version
    [Tags]    release    critical
    Verify Release    ${EXPECTED_VERSION}
