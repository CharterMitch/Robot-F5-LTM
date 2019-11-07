*** Settings ***
# https://clouddocs.f5.com/api/icontrol-soap/LocalLB__LBMethod.html
Resource    ../common.resource
Library     ../F5Rest.py  ${f5_primary}     ${user}

*** Test Cases ***
Show Net Interface
    [Documentation]         Log interface properties.
    ${var}=                 tmsh show net interface all-properties
    Log                     ${var}

Show Net Trunk
    [Documentation]         Log trunk information, validate trunks are up.
    ${var}=                 tmsh show net trunk
    Log                     ${var}
    # Validate UplinkTrunk and HA_trunk are in up state
    Should Match Regexp     ${var}   UplinkTrunk .+up
    Should Match Regexp     ${var}   HA_trunk .+up

Disable Interface
    [Documentation]         Disable an interface and validate it goes offline.
    [Setup]                 tmsh modify net interface 2.1 disabled
    Sleep                   2
    ${var}=                 tmsh show net interface 2.1
    Log                     ${var}
    Should Match Regexp     ${var}   2.1 .+disabled
    [Teardown]              tmsh modify net interface 2.1 enabled

Trunk bandwidth decreases with interface down
    [Documentation]         With an interface disabled, bandwidth of trunk should decrease.
    [Setup]                 tmsh modify net interface 2.1 disabled
    Sleep                   2
    ${var}=                 tmsh show net trunk UplinkTrunk
    Log                     ${var}
    # Bandwidth should be 10G with one interface down
    Should Match Regexp     ${var}   up.+10000
    [Teardown]              tmsh modify net interface 2.1 enabled

Enable Interface
    [Documentation]         Enable an interface and validate it comes online
    [Setup]                 tmsh modify net interface 2.1 enabled
    Sleep                    2
    ${var}=                 tmsh show net interface 2.1
    Log                     ${var}
    Should Match Regexp     ${var}   2.1 .+up
    [Teardown]              None