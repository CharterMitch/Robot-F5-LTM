*** Settings ***
# https://clouddocs.f5.com/api/icontrol-soap/LocalLB__LBMethod.html
Resource    ../common.resource
Variables   settings.yaml
Library     ../F5Rest.py  ${f5_a}   ${user}

*** Test Cases ***
V4 Default Route
    [Documentation]     Verify we received default route from upstream peer.
    ${result}           imish -c 'show ip route 0.0.0.0'
    Should contain      ${result}   Known via "bgp"
    Log                 ${result}   

V6 Default Route
    [Documentation]     Verify we received default route from upstream peer.
    ${result}           imish -c 'show ipv6 route ::/0'
    Should contain      ${result}   Known via "bgp"
    Log                 ${result} 

V4 Static Route
    [Documentation]     Verify V4 static route is advertised.
    imish -c 'enable','conf t','ip route ${v4_static} null'
    Sleep               3
    ${result}           imish -c 'show ip route ${v4_static}'
    Should contain      ${result}   Known via "static"
    ${result}           imish -c 'show ip bgp ${v4_static}'
    # Advertised to peer groups: output should have our IPV4 peer group listed
    Should contain      ${result}   IPV4-NORTHSIDE-PG
    Log                 ${result}
    imish -c 'enable','conf t','no ip route ${v4_static} null'

V6 Static Route
    [Documentation]     Verify V6 static route is advertised.
    imish -c 'enable','conf t','ipv6 route ${v6_static} null'
    Sleep               3
    ${result}           imish -c 'show ip route ${v6_static}'
    Should contain      ${result}   Known via "static"
    ${result}           imish -c 'show ip bgp ${v6_static}'
    # Advertised to peer groups: output should have our IPV4 peer group listed
    Should contain      ${result}   IPV4-NORTHSIDE-PG
    Log                 ${result}
    imish -c 'enable','conf t','no ipv6 route ${v6_static} null'