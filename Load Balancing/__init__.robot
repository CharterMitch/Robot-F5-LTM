*** Settings ***
Documentation    Load Balancing method tests
Resource        ../common.resource
Suite Setup     Setup virtual server
Suite Teardown  Teardown virtual server

*** Variables ***
${pool}             http_test_pool
@{nodes}            198.18.64.11     198.18.64.12
${virtual_server}   198.18.32.1

*** Keywords ***
Setup virtual server
    [Documentation]     Setup a basic http virtual server to use in the 
    ...                 HTTP load balancing test cases.
    [tags]  Setup
    Connect To F5   ${f5_a}     ${USER}
    Create nodes ${nodes}
    Create pool ${pool} using ${nodes} and port 80
    Create http virtual server ${virtual_server} ip ${virtual_server} pool ${pool} port 80
    Set route advertisement ${virtual_server}

Teardown virtual server
    [Documentation]     Teardown all of the configuration used for the HTTP testing.
    [tags]  Teardown
    Delete virtual server ${virtual_server}
    Delete pool ${pool}
    Delete nodes ${nodes}