*** Settings ***
Resource        ../common.resource
Library         ../F5Rest.py  ${f5_primary}     ${user}
Library         Dialogs
Library         SSHLibrary
Library         Telnet


*** Test Cases ***
Telnet Connection Fails
    [Documentation]     Make sure telnet to the F5 fails.
    Run Keyword And Expect Error    ConnectionRefusedError:*  telnet.Open Connection    ${f5_primary}[host]

SSH Connection
    [Documentation]     SSH connection is established.
    sshlibrary.open connection     ${f5_primary}[host]
    [Teardown]          sshlibrary.close all connections
