*** Settings ***
Resource    ../../common.resource
Library     ../../F5Rest.py    ${f5_primary}   ${user}
Variables   ../settings.yaml

*** Keywords ***
IXIA Stats as Pandas df
    [Documentation]     Gather IXIA test stats for the currently running test
    ...                 then return the data as a pandas dataframe (df).
    ${stats}=           Gather IXLoad Stats
    ${df}=              Convert to dataframe ${stats}
    [Return]            ${df}

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
    [Setup]                 Run Keywords    Start Ixia Test     v4_https.rxf
    ...                     AND             tmsh reset-stats ltm virtual
    ...                     AND             tmsh reset-stats ltm pool
    ...                     AND             tmsh reset-stats ltm profile client-ssl clientssl   
    ${df}=                  IXIA Stats as Pandas df
    @{cols}=                Create List     HTTP Concurrent Connections    HTTP Simulated Users    HTTP Requests Failed
    HTML Chart              ${df}   ${cols}
    ${result}=              tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    # TLS 1.2 connections should be in the thousands or millions
    Should Match Regexp     ${result}   Version 1.2.+\[KM\]\n
    [Teardown]              Run Keywords    Stop Ixia Test
    ...                     AND             Log F5 Pool Data    ${pool}     ${virtual_server}

V6 SSL Offload
    [Documentation]         SSL Offload V6 HTTP Traffic
    [Setup]                 Run Keywords    Start Ixia Test     v6_https.rxf
    ...                     AND             tmsh reset-stats ltm virtual
    ...                     AND             tmsh reset-stats ltm pool
    ...                     AND             tmsh reset-stats ltm profile client-ssl clientssl                   
    ${df}=                  IXIA Stats as Pandas df
    @{cols}=                Create List     HTTP Concurrent Connections    HTTP Simulated Users    HTTP Requests Failed
    HTML Chart              ${df}   ${cols}
    ${result}=              tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    # TLS 1.2 connections should be in the thousands or millions
    Should Match Regexp     ${result}   Version 1.2.+\[KM\]\n
    [Teardown]              Run Keywords    Stop Ixia Test
    ...                     AND             Log F5 Pool Data    ${pool}     ${virtual_server}