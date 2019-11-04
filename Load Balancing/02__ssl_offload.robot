*** Settings ***
Resource    ../common.resource
Library     ../F5Rest.py    ${f5_a}   ${user}
Variables   settings.yaml

*** Test Cases ***
V4 SSL Offload
    Reset Statistics
    Log v4 Statistics
    ${result}=     tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    # TLS 1.2 should be at 0 connections
    Should Match Regexp     ${result}   Version 1.2.+0\n
    # Start IXIA Test
    # Wait until test completes
    ${result}=     tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    # Should be thousands of connections "K"
    Should Match Regexp     ${result}   Version 1.2.+K\n
    &{stats}=   Get pool ${pool} stats
    Log v4 Statistics

V6 SSL Offload
    Reset Statistics
    Log Statistics
    ${result} =     tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    # TLS 1.2 should be at 0 connections
    Should Match Regexp     ${result}   Version 1.2.+0\n
    # Start IXIA Test
    # Wait until test completes
    # Verify connections > 25K?
    ${result} =     tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    # TLS 1.2 should have thousands of connections "K"
    Should Match Regexp     ${result}   Version 1.2.+K\n

*** Keywords ***
Reset Statistics
    [Documentation]     Reset various statistics on the F5.
    tmsh reset-stats ltm virtual
    tmsh reset-stats ltm pool
    tmsh reset-stats ltm profile client-ssl clientssl

Log v4 Statistics
    [Documentation]     Log statistics.
    ${v1}=  tmsh show ltm pool ${v4_pool}
    ${v2}=  tmsh show ltm virtual ${virtual_server}
    ${v3}=  tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    Log Many    ${v1}   ${v2}   ${v3}

Log v6 Statistics
    [Documentation]     Log statistics.
    ${v1}=  tmsh show ltm pool ${v6_pool}
    ${v2}=  tmsh show ltm virtual ${v4_virtual_server}
    ${v3}=  tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    Log Many    ${v1}   ${v2}   ${v3}