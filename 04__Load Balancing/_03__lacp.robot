*** Settings ***
Resource    ../common.resource
Library     ../F5Rest.py  ${f5_primary}     ${user}

*** Test Cases ***
Port-channel Load Balancing
    [Documentation]     Verify port-channel load-balancing.
    [Setup]             Start Ixia Test     v4_http.rxf
    # Reset interface statistics
    tmsh reset net interface
    tmsh show net interface all-properties | grep Uplink
    # Run load for 2 minutes
    tmsh show net interface all-properties | grep Uplink
    # Compare interface results ...