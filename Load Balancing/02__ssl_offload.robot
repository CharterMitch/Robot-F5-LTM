*** Settings ***
Resource    ../common.resource
Library     ../F5Rest.py    ${f5_a}   ${user}
Variables   settings.yaml

*** Test Cases ***
V4 SSL Offload
    Reset Statistics
    Log Statistics
    ${result} =     tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    # TLS 1.2 should be at 0 connections
    Should Match Regexp     ${result}   Version 1.2.+0\n
    # Start IXIA Test
    # Wait until test completes
    # Verify connections > 25K?

*** Keywords ***
Reset Statistics
    [Documentation]     Reset statistics on the F5.
    tmsh reset-stats ltm virtual
    tmsh reset-stats ltm pool
    tmsh reset-stats ltm profile client-ssl clientssl

Log Statistics
    [Documentation]     Log statistics.
    ${v1}=  tmsh show ltm pool ${pool}
    ${v2}=  tmsh show ltm virtual ${virtual_server}
    ${v3}=  tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    Log Many    ${v1}   ${v2}   ${v3}