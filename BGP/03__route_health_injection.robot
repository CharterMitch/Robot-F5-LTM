*** Settings ***
# https://clouddocs.f5.com/api/icontrol-soap/LocalLB__LBMethod.html
Resource    ../common.resource
Variables   settings.yaml
Library     ../F5Rest.py  ${f5_a}   ${user}

*** Test Cases ***
Test V4 SSL Offload
    Reset Statistics
    ${result} = tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    # TLS 1.2 should be at 0 Connections
    Should Match Regexp     ${result}   Version 1.2\t+0$
    # Start IXIA Test
    # Log Stats

Test V6 Route Health Injection
    Reset Statistics

V4 Static Route
    [Documentation]     Verify V4 static route is advertised.
    imish -c 'enable','conf t','ip route ${v4_static} null'
    # Wait                          Wait for    Retry every     Commmand
    Wait until keyword succeeds     30 sec      2 sec           v4 route exists  ${v4_static} 
    ${result}           imish -c 'show ip route ${v4_static}'
    Should contain      ${result}   Known via "static"
    ${result}           imish -c 'show ip bgp ${v4_static}'
    # Advertised to peer groups: output should have our IPV4 peer group listed
    Should contain      ${result}   ${v4_peer_group}
    Log                 ${result}
    imish -c 'enable','conf t','no ip route ${v4_static} null'

V6 Static Route
    [Documentation]     Verify V6 static route is advertised.
    imish -c 'enable','conf t','ipv6 route ${v6_static} null'
    # Wait                          Wait for    Retry every     Commmand
    Wait until keyword succeeds     30 sec      2 sec           v6 route exists  ${v6_static} 
    ${result}           imish -c 'show ipv6 route ${v6_static}'
    Should contain      ${result}   Known via "static"
    ${result}           imish -c 'show bgp ${v6_static}'
    # Advertised to peer groups: output should have our IPV4 peer group listed
    Should contain      ${result}   ${v6_peer_group}
    Log                 ${result}
    imish -c 'enable','conf t','no ipv6 route ${v6_static} null'


