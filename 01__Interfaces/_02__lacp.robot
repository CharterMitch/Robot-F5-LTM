*** Settings ***
Resource    ../common.resource
Library     ../F5Rest.py  ${f5_primary}     ${user}

*** Test Cases ***
Port-channel Load Balancing
    [Documentation]
    [Setup]         Start Ixia Test     lacp_test.rxf
    # Reset interface statistics
    tmsh reset net interface
    tmsh show net interface all-properties | grep Uplink
    # Run load for 2 minutes
    Sleep   120
    tmsh show net interface all-properties | grep Uplink
    # Compare interface results ...