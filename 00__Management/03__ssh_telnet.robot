*** Settings ***
Resource        ../common.resource
Library         ../F5Rest.py  ${f5_primary}     ${user}
Library         Dialogs
Library         SSHLibrary
Library         Telnet

*** Test Cases ***
Telnet Connection Fails
    [Documentation]     Telnet to the F5 fails.
    Run Keyword And Expect Error    ConnectionRefusedError:*  telnet.Open Connection    ${f5_primary}[host]

SSH Connection
    [Documentation]     SSH connection is established.
    sshlibrary.open connection     ${f5_primary}[host]
    sshlibrary.login    ${user}[username]   ${user}[password]
    [Teardown]          sshlibrary.close all connections

SSH ACL
    [Documentation]     Verify management SSH ACL blocks connections.
    [Setup]             tmsh modify sys sshd allow delete { ALL }
    sshlibrary.open connection      ${f5_primary}[host]
    Run Keyword And Expect Error    SSHException:*     sshlibrary.login    test   test
    [Teardown]          tmsh modify sys sshd allow add { ALL }
