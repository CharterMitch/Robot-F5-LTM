*** Settings ***
# https://clouddocs.f5.com/api/icontrol-soap/LocalLB__LBMethod.html
Resource    ../common.resource
Library     ../F5Rest.py  ${f5_primary}     ${user}

*** Test Cases ***
Show net lldp-neighbors
    [Documentation]
    ${var}=     tmsh show net lldp-neighbors all-properties
    Log         ${var}