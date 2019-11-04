*** Settings ***
Documentation    Load Balancing method tests
Resource        ../common.resource
Variables       settings.yaml
Library         ../F5Rest.py  ${f5_primary}     ${user}
Suite Setup     Setup F5
Suite Teardown  Teardown

*** Keywords ***
Setup F5
    [Documentation]     Setup a basic http virtual server to use in 
    ...                 load balancing test cases.
    [tags]  Setup
    tmsh create ltm node ${node_1} address ${node_1}
    tmsh create ltm node ${node_2} address ${node_2}
    tmsh create ltm pool ${pool} { members add { ${node_1}:80 ${node_2}:80 } monitor none }
    tmsh create ltm virtual ${virtual_server} destination ${virtual_server}:80 mask 255.255.255.255 ip-protocol tcp pool ${pool}
    tmsh modify ltm virtual-address 198.18.32.1 route-advertisement selective

Teardown
    [Documentation]     Teardown the configuration for this test suite.
    [tags]  Teardown
    tmsh delete ltm virtual ${virtual_server}
    tmsh delete ltm pool ${pool}
    tmsh delete ltm node ${node_1}
    tmsh delete ltm node ${node_2}