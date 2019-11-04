*** Settings ***
Documentation    Load Balancing method tests
Resource        ../common.resource
Library         ../F5Rest.py  ${f5_primary}     ${user}
Library         ../F5.py
Variables       settings.yaml
Suite Setup     Setup F5
Suite Teardown  Teardown

*** Keywords ***
Setup F5
    [Documentation]     Setup a basic http virtual server to use in 
    ...                 load balancing test cases.
    [tags]  Setup
    # Run all tmsh commands from f5.tmsh
    Connect To F5   ${f5_primary}     ${user}
    tmsh create ltm node ${node_1} address ${node_1}
    tmsh create ltm node ${node_2} address ${node_2}
    tmsh create ltm pool ${pool} { members add { ${node_1}:80 ${node_2}:80 } monitor none }
    tmsh create ltm virtual ${virtual_server} destination ${virtual_server}:80 mask 255.255.255.255 ip-protocol tcp pool ${pool}
    tmsh modify ltm virtual-address 198.18.32.1 route-advertisement selective

Teardown
    [Documentation]     Teardown the configuration for this test suite.
    [tags]  Teardown
    Delete virtual server ${virtual_server}
    Delete pool ${pool}
    Delete nodes ${nodes}