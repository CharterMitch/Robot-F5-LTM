*** Settings ***
Resource    ../common.resource
Library     ../F5Rest.py  ${f5_primary}     ${user}

*** Test Cases ***
Show net vlan
    ${var}=     tmsh show net vlan all-properties
    Log         ${var}
