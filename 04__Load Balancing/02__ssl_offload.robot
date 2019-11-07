*** Settings ***
Resource    ../common.resource
Library     ../F5Rest.py    ${f5_primary}   ${user}
Variables   settings.yaml
Resource    suite.resource


*** Test Cases ***
V4 SSL Offload
    [Documentation]         SSL Offload V4 HTTP Traffic
    [Setup]                 Start Ixia Test     v4_https.rxf
    Reset Statistics
    Log F5 Statistics       ${pool}     ${virtual_server}
    # Wait a while for ixia test traffic
    Sleep                   60
    ${result}=              tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    # TLS 1.2 connections should be in the thousands. Example: Version 1.2   12K
    Should Match Regexp     ${result}   Version 1.2  .+K\n
    Log F5 Statistics       ${pool}     ${virtual_server}
    [Teardown]              Stop Ixia Test

V6 SSL Offload
    [Documentation]         SSL Offload V6 HTTP Traffic
    [Setup]                 Start Ixia Test     v6_https.rxf          
    Reset Statistics
    Log F5 Statistics       ${pool}     ${virtual_server}
    # Wait a while for ixia test traffic
    Sleep                   60
    ${result} =             tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    # TLS 1.2 connections should be in the thousands. Example: Version 1.2   12K
    Should Match Regexp     ${result}   Version 1.2  .+K\n
    Log F5 Statistics       ${pool}     ${virtual_server}
    [Teardown]              Stop Ixia Test 