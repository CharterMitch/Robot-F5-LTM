*** Settings ***
Documentation    VLAN Testing
Resource        ../common.resource

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