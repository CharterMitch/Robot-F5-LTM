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
    [Documentation]     Configure BGP peering.
    [tags]  Setup
    ${result}     secondary.zebos -c 'show ip bgp summary'
    Log     Secondary F5: ${result}
    ${result}     primary.zebos -c 'show ip bgp summary'
    Log     Primary F5: ${result}
    # Router bgp ${as_number}
    # Add v4 peers ${bgp_peers_ipv4}
    # Add v6 peers ${bgp_peers_ipv6}

Teardown
    [Documentation]     Teardown the configuration for this test suite.
    [tags]  Teardown
    # No router bgp ${as_number}
    Log     'Not implemented.'