*** Settings ***
# https://clouddocs.f5.com/api/icontrol-soap/LocalLB__LBMethod.html
Resource    ../common.resource
Library     ../F5Rest.py  ${f5_primary}     ${user}

*** Test Cases ***
Create Port-channel
    [Documentation]
    No Operation

Remove port-channel member
    [Documentation]
    No Operation

Test Load
    [Documentation]
    No Operation

Add port-channel member
    [Documentation]
    No Operation