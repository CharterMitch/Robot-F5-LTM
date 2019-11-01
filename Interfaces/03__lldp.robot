*** Settings ***
# https://clouddocs.f5.com/api/icontrol-soap/LocalLB__LBMethod.html
Resource    ../common.resource
Variables   settings.yaml
Library     ../F5Rest.py  ${f5_a}   ${user}

*** Test Cases ***
Enable LLDP
    [Documentation]
    No Operation

Verify LLDP Neighbor
    [Documentation]
    No Operation