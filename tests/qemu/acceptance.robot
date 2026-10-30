*** Settings ***
Library    target_keywords.py

*** Variables ***
${EXPECTED_VERSION}    %{EXPECTED_VERSION=0.1.5}

*** Test Cases ***
temperature_input__normal_reading
    [Tags]    temperature_input
    Verify Reading    25    NORMAL

temperature_input__critical__overheat_boundary
    [Tags]    temperature_input    critical
    Verify Reading    80    OVERHEAT

threshold_control__critical__custom_threshold
    [Tags]    threshold_control    critical
    Verify Reading    25    OVERHEAT    20

threshold_control__critical__invalid_threshold
    [Tags]    threshold_control    critical
    Verify Invalid Threshold    126

fault_diagnostics__critical__out_of_range_reading
    [Tags]    fault_diagnostics    critical
    Verify Invalid Reading    -41

firmware_identity__critical__expected_version
    [Tags]    firmware_identity    critical
    Verify Release    ${EXPECTED_VERSION}
