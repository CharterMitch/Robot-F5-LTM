*** Settings ***
# https://clouddocs.f5.com/api/icontrol-soap/LocalLB__LBMethod.html
Resource    ../common.resource

*** Test Cases ***
Verify 9000 MTU
    [Documentation]
    # Set VLAN MTU to 9000
    # Pass IXIA traffic at MTU 9000
    No Operation