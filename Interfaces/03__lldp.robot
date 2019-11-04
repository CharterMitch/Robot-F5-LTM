*** Settings ***
# https://clouddocs.f5.com/api/icontrol-soap/LocalLB__LBMethod.html
Resource    ../common.resource

*** Test Cases ***
Enable LLDP
    [Documentation]
    No Operation

Verify LLDP Neighbor
    [Documentation]
    No Operation