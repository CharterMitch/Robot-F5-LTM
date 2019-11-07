*** Settings ***
Resource    ../common.resource
Library     ../F5Rest.py  ${f5_primary}     ${user}

*** Test Cases ***
Port-channel Load Balancing
    [Documentation]
    [Setup]         Start Ixia Test     lacp_test.rxf
    # Reset interface statistics
    tmsh reset net interface
    ${var}          tmsh show net interface all-properties | grep Uplink
    Log             ${var}
    # Let Traffic Load-balance across links
    Sleep           60
    ${var}          tmsh show net interface all-properties | grep Uplink
    Log             ${var}