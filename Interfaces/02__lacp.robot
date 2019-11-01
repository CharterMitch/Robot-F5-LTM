*** Settings ***
# https://clouddocs.f5.com/api/icontrol-soap/LocalLB__LBMethod.html
Resource    ../common.resource
Variables   settings.yaml
Library     ../F5Rest.py  ${f5_a}   ${user}

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