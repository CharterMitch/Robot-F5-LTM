*** Settings ***
# https://clouddocs.f5.com/api/icontrol-soap/LocalLB__LBMethod.html
Resource    ../common.resource

*** Test Cases ***
Show net vlan
    ${var}=     tmsh show net vlan all-properties
    Log         ${var}
