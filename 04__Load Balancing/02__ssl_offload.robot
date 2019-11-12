*** Settings ***
Resource    ../common.resource
Library     ../F5Rest.py    ${f5_primary}   ${user}
Variables   settings.yaml

*** Keywords ***
Build Ixia Chart
    [Documentation]     Gather IXIA test stats for the currently running test
    ...                 then return an HTML graph.
    ${stats}=           Gather IXLoad Stats
    @{graph}=           Create List      HTTP Concurrent Connections    HTTP Simulated Users    HTTP Requests Failed
    ${chart}=           IXLoad Chart ${stats} ${graph}
    [Return]            ${chart}

Reset Statistics
    [Documentation]     Reset various statistics on the F5.
    ${test}=            tmsh reset-stats ltm virtual
    tmsh reset-stats ltm pool
    tmsh reset-stats ltm profile client-ssl clientssl

Log F5 Pool Data
    [Documentation]     Log virtual server, pool, member and profile statistics.
    [Arguments]         ${pool}     ${virtual_server}
    tmsh show ltm pool ${pool}
    tmsh show ltm pool ${pool} members
    tmsh show ltm virtual ${virtual_server}
    tmsh show ltm profile client-ssl clientssl | grep -i Protocol

*** Test Cases ***
V4 SSL Offload
    [Documentation]         SSL Offload V4 HTTP Traffic
    [Setup]                 Start Ixia Test     v4_https.rxf
    Reset Statistics
    ${chart}=               Build Ixia Chart
    Log                     ${chart}    HTML
    ${result}=              tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    # TLS 1.2 connections should be in the thousands. Example: Version 1.2   12K
    Should Match Regexp     ${result}   Version 1.2  .+K\n
    Log F5 Pool Data        ${pool}     ${virtual_server}
    [Teardown]              Stop Ixia Test

V6 SSL Offload
    [Documentation]         SSL Offload V6 HTTP Traffic
    [Setup]                 Start Ixia Test     v6_https.rxf          
    Reset Statistics
    ${chart}=               Build Ixia Chart
    Log                     ${chart}    HTML
    ${result} =             tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    # TLS 1.2 connections should be in the thousands. Example: Version 1.2   12K
    Should Match Regexp     ${result}   Version 1.2  .+K\n
    Log F5 Pool Data        ${pool}     ${virtual_server}
    [Teardown]              Stop Ixia Test 