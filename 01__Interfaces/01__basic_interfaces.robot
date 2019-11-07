*** Settings ***
# https://clouddocs.f5.com/api/icontrol-soap/LocalLB__LBMethod.html
Resource    ../common.resource
Library     ../F5Rest.py  ${f5_primary}     ${user}

*** Test Cases ***
Show Net Interface
    ${var}=     tmsh show net interface
    Log         ${var}

Show Net Trunk
    ${var}=     tmsh show net trunk
    Log         ${var}
    # Validate UplinkTrunk is in up state
    Should Match Regexp     ${var}   UplinkTrunk .+up

Disable Interface
    [Documentation]
    No Operation

Enable Interface
    [Documentation]
    No Operation