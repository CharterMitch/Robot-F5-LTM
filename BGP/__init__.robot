*** Settings ***
Documentation    BGP Routing Protocol Tests
Resource        ../common.resource
Library         ../F5Rest.py  ${f5_a}   ${user}     WITH NAME  primary
Library         ../F5Rest.py  ${f5_b}   ${user}     WITH NAME  secondary
Variables       settings.yaml
Suite Setup     Setup F5
#Suite Teardown  Teardown

*** Keywords ***
Setup F5
    [Documentation]     Setup for the F5 BGP routing tests.
    [tags]  Setup
    # Router bgp ${as_number}
    # Add v4 peers ${bgp_peers_ipv4}
    Add v4 peers
    Log Configuration

Add v4 peers
    [Documentation]     Add IPv4 Peers to the ZebOS Configuration
    :for    ${neighbor}     IN  @{v4_peers}
    \   primary.imish -c 'enable','conf t','router bgp ${asn}','neighbor ${neighbor} peer-group ${v4_peer_group}'
    \   primary.imish -c 'enable','conf t','router bgp ${asn}','address-family ipv4','neighbor ${neighbor} activate'
    \   secondary.imish -c 'enable','conf t','router bgp ${asn}','neighbor ${neighbor} peer-group ${v4_peer_group}'
    \   secondary.imish -c 'enable','conf t','router bgp ${asn}','address-family ipv4','neighbor ${neighbor} activate'

Add v6 peers
    [Documentation]     Add IPv6 Peers to the ZebOS Configuration
    :for    ${neighbor}     IN  @{v6_peers}
    \   primary.imish -c 'enable','conf t','router bgp ${asn}','neighbor ${neighbor} peer-group ${v6_peer_group}'
    \   primary.imish -c 'enable','conf t','router bgp ${asn}','address-family ipv6','neighbor ${neighbor} activate'
    \   secondary.imish -c 'enable','conf t','router bgp ${asn}','neighbor ${neighbor} peer-group ${v6_peer_group}'
    \   secondary.imish -c 'enable','conf t','router bgp ${asn}','address-family ipv6','neighbor ${neighbor} activate'

Log Configuration
    [Documentation]     Log the running imish configuration from primary
    ...                 and secondary F5 devices.
    [tags]  Setup   
    ${result}       primary.imish -c 'show run'
    Log             Primary F5: ${result}
    ${result}       secondary.imish -c 'show run'
    Log             Secondary F5: ${result}

Teardown
    [Documentation]     Teardown the configuration for this test suite.
    [tags]  Teardown
    # No router bgp ${as_number}
    Log     'Not implemented.'