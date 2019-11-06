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
    Log v6 Statistics
    ${result} =     tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    # TLS 1.2 should be at 0 connections
    Should Match Regexp     ${result}   Version 1.2.+0\n
    Sleep   120
    # Verify connections > 25K?
    ${result} =     tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    # TLS 1.2 should have thousands of connections "K"
    Should Match Regexp     ${result}   Version 1.2.+K\n