*** Settings ***
Documentation    BGP Routing Protocol Tests
Resource        ../common.resource
Library         ../F5Rest.py  ${f5_a}   ${user}     WITH NAME  primary
Library         ../F5Rest.py  ${f5_b}   ${user}     WITH NAME  secondary
Variables       settings.yaml
#Suite Setup     Setup F5
#Suite Teardown  Teardown

*** Keywords ***
Setup F5
    [Documentation]     Setup F5 for VLAN tests.
    [tags]  Setup
    # Create VLAN with tag

Teardown
    [Documentation]     Teardown the configuration for this test suite.
    [tags]  Teardown
    #Delete vlan