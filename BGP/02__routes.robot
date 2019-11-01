*** Settings ***
# https://clouddocs.f5.com/api/icontrol-soap/LocalLB__LBMethod.html
Resource    ../common.resource
Variables   settings.yaml
Library     ../F5Rest.py  ${f5_a}   ${user}

*** Test Cases ***
V4 Default Route
    [Documentation]     Verify we received default route from upstream peer.
    ${result}           imish -c 'show ip route 0.0.0.0'
    Should contain      ${result}    Known via "bgp"
    Log                 ${result}   

V6 Default Route
    [Documentation]     Verify we received default route from upstream peer.
    ${result}           imish -c 'show ipv6 route ::/0'
    Should contain      ${result}    Known via "bgp"
    Log                 ${result} 