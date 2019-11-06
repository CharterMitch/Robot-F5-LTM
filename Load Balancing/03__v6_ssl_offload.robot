*** Settings ***
Resource    ../common.resource
Library     ../F5Rest.py    ${f5_primary}   ${user}
Variables   settings.yaml
Resource    suite.resource
Suite Setup     Start Ixia Test     v6_https.rxf
Suite Teardown  Stop Ixia Test

*** Test Cases ***
V6 SSL Offload
    Reset Statistics
    Log F5 Statistics       ${pool}     ${virtual_server}
    # Wait a while for ixia test traffic
    Sleep   60
    ${result} =     tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    # TLS 1.2 connections should be in the thousands. Example: Version 1.2   12K
    Should Match Regexp     ${result}   Version 1.2.+K\n
    Log F5 Statistics       ${pool}     ${virtual_server}