*** Settings ***
Documentation    Interface, Trunk and LACP testing
Resource        ../common.resource
#Library         ../F5Rest.py  ${f5_a}   ${user}     WITH NAME  primary
#Library         ../F5Rest.py  ${f5_b}   ${user}     WITH NAME  secondary
#Suite Setup     Setup F5
#Suite Teardown  Teardown

*** Keywords ***
Setup F5
    [Documentation]     Setup the F5 for interface testing.
    [tags]  Setup
    No Operation

Teardown
    [Documentation]     Teardown the configuration for this test suite.
    [tags]  Teardown
    No Operation