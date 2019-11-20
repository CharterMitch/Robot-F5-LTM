*** Settings ***
Resource    ../common.resource
Variables   settings.yaml
Library     ../F5Rest.py  ${f5_primary}   ${user}

*** Test Cases ***
V4 Default Route
    [Documentation]     Verify we received default route from upstream peer.
    ${result}           imish -c 'show ip route 0.0.0.0'
    Should contain      ${result}   Known via "bgp" 

V6 Default Route
    [Documentation]     Verify we received default route from upstream peer.
    ${result}           imish -c 'show ipv6 route ::/0'
    Should contain      ${result}   Known via "bgp"

V4 Static Route
    [Documentation]     Verify V4 static route is advertised.
    [Setup]             imish -c 'enable','conf t','ip route ${v4_static} null'
    # Wait                          Wait for    Retry every     Commmand
    Wait until keyword succeeds     30 sec      2 sec           v4 route exists  ${v4_static}
    Sleep               5 
    ${result}           imish -c 'show ip route ${v4_static}'
    Should contain      ${result}   Known via "static"
    ${result}           imish -c 'show ip bgp ${v4_static}'
    # Advertised to peer groups: output should have our IPV4 peer group listed
    Should contain      ${result}   ${v4_peer_group}
    [Teardown]          imish -c 'enable','conf t','no ip route ${v4_static} null'

V6 Static Route
    [Documentation]     Verify V6 static route is advertised.
    [Setup]             imish -c 'enable','conf t','ipv6 route ${v6_static} null'
    # Wait                          Wait for    Retry every     Commmand
    Wait until keyword succeeds     30 sec      2 sec           v6 route exists  ${v6_static} 
    Sleep               5 
    ${result}           imish -c 'show ipv6 route ${v6_static}'
    Should contain      ${result}   Known via "static"
    ${result}           imish -c 'show bgp ${v6_static}'
    # Advertised to peer groups: output should have our IPV4 peer group listed
    Should contain      ${result}   ${v6_peer_group}
    [Teardown]          imish -c 'enable','conf t','no ipv6 route ${v6_static} null'

*** Keywords ***
v4 route exists
    [Documentation]     Verify a route is in the routing table.
    [Arguments]         ${route}
    ${result}           imish -c 'show ip route ${route}'
    Should contain      ${result}   Routing entry

v6 route exists
    [Documentation]     Verify a route is in the routing table.
    [Arguments]         ${route}
    ${result}           imish -c 'show ipv6 route ${route}'
    Should contain      ${result}   Routing entry