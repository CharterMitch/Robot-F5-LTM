*** Settings ***
Documentation    Load Balancing method tests
Resource        ../common.resource
Library         ../F5.py
Variables       settings.yaml
Suite Setup     Setup F5
#Suite Teardown  Teardown

*** Keywords ***
Setup F5
    [Documentation]     Setup a basic http virtual server to use in 
    ...                 load balancing test cases.
    [tags]  Setup
    # Run all tmsh commands from f5.tmsh
    Connect To F5   ${f5_primary}     ${user}
    Create nodes ${nodes}
    Create pool ${pool} using ${nodes} and port 80
    Create http virtual server ${virtual_server} ip ${virtual_server} pool ${pool} port 80
    Set route advertisement ${virtual_server}

Teardown
    [Documentation]     Teardown the configuration for this test suite.
    [tags]  Teardown
    Delete virtual server ${virtual_server}
    Delete pool ${pool}
    Delete nodes ${nodes}