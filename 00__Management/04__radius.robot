*** Settings ***
Resource        ../common.resource
Library         ../F5Rest.py  ${f5_primary}     ${user}
Library         Dialogs
Library         SSHLibrary
Suite Setup     Configure Radius
Suite Teardown  Unconfigure Radius

*** Variables ***
${root_password}        default
${audit_password}       password

*** Test Cases ***
Root login
    [Documentation]         Test root login.   
    #${password}            Get value from user     root password:    default
    SSH to F5               ${f5_primary}[host]   root   ${root_password}
    ${output}=              Execute Command     whoami
    Should be equal         ${output}   root
    [Teardown]              Close all connections

Auditor role
    [Documentation]         Test auditor login and that the proper role is assigned.
    #${password}             Get value from user     f5dnaRO password:    password
    SSH to F5               ${f5_secondary}[host]   f5dnaRO   ${audit_password}
    ${output}=              Execute Command     show auth user field-fmt
    Should match regexp     ${output}   role auditor
    ${create_rc}=           Execute Command     ltm create node test address 1.1.1.1    return_stdout=False     return_rc=True
    # Return code should be 1 "fail"
    Should Be Equal As Integers     ${create_rc}  1
    [Teardown]              Close all connections

*** Keywords ***
SSH to F5
    [Documentation]     Connect to an F5 BIG-IP via SSH
    [Arguments]         ${host}         ${username}     ${password}
    Open connection     ${host}
    Login               ${username}     ${password}

Configure Radius
    [Documentation]     Add radius servers and roles to the F5s.
    tmsh create auth radius-server RADIUS-ISE1 secret l1v3l0ng server 66.189.243.4
    tmsh create auth radius-server RADIUS-ISE2 secret l1v3l0ng server 66.189.243.5
    tmsh modify auth remote-role role-info add { admin_group { attribute F5-LTM-User-Role=Administrator console tmsh line-order 1001 role administrator user-partition All } }
    tmsh modify auth remote-role role-info add { audit_group { attribute F5-LTM-User-Role=Auditor console tmsh line-order 1002 role auditor user-partition All } }
    tmsh modify auth source { type radius }
    tmsh create sys management-route radius gateway 10.240.72.1 network 66.189.243.0/24

Unconfigure Radius
    [Documentation]     Remove radius configuration.
    tmsh delete auth radius-server RADIUS-ISE1
    tmsh delete auth radius-server RADIUS-ISE2
    tmsh modify auth remote-role role-info delete {admin_group}
    tmsh modify auth remote-role role-info delete {audit_group}
    tmsh delete sys management-route radius
