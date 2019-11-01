*** Settings ***
# https://clouddocs.f5.com/api/icontrol-soap/LocalLB__LBMethod.html
Resource    ../common.resource
Variables   settings.yaml
Library     ../F5Rest.py  ${f5_a}   ${user}

*** Test Cases ***
Verify 9000 MTU
    [Documentation]
    # Set MTU to 9000
    # Pass IXIA traffic at MTU 9000
    No Operation