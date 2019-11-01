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
    # Add v6 peers ${bgp_peers_ipv6}
    Log Configuration

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