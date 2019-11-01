*** Settings ***
Documentation    BGP Routing Protocol Tests
Resource        ../common.resource
Variables       settings.yaml
Suite Setup     Setup F5
Suite Teardown  Teardown

*** Keywords ***
Setup F5
    [Documentation]     Configure BGP peering.
    [tags]  Setup
    Connect To F5   ${f5_a}     ${user}
    # Router bgp ${as_number}
    # Add v4 peers ${bgp_peers_ipv4}
    # Add v6 peers ${bgp_peers_ipv6}

Teardown
    [Documentation]     Teardown the configuration for this test suite.
    [tags]  Teardown
    # No router bgp ${as_number}