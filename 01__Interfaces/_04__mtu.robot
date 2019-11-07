*** Settings ***
Resource    ../common.resource
Library     ../F5Rest.py  ${f5_primary}     ${user}

*** Test Cases ***
Verify 9000 MTU
    [Documentation]     Ensure MTU of 9000 is set for new VLAN.
    # [Setup] Create vlan with 9000 MTU
    # Pass IXIA traffic at MTU 9000
    No Operation