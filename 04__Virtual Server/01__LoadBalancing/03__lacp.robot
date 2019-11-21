*** Settings ***
# This test included under virtual server testing as passing traffic
# through the F5s often requires Virtual Servers in one way or another.
Resource    ../../common.resource
Library     ../../F5Rest.py  ${f5_primary}     ${user}
Library     String

*** Variables ***
${network}      198.18.32.0
${mask}         255.255.255.0
${cidr}         198.18.32.0/24

*** Test Cases ***
Interface Load Balancing
    [Documentation]     Verify port-channel load-balancing.
    ...                 Port 2.1 and 2.2 should have equal bandwidth.
    [Setup]             Setup Test
    ${int_1}=           Get interface stats 2.1
    ${int_2}=           Get interface stats 2.2
    ${diff_in}=         Percentage difference ${int_1.counters_bitsIn.value} ${int_2.counters_bitsIn.value}
    ${diff_out}=        Percentage difference ${int_1.counters_bitsOut.value} ${int_2.counters_bitsOut.value}
    # Allow 10% difference between interfaces
    Should be true      ${diff_in}<10
    Should be true      ${diff_out}<10
    [Teardown]          Teardown Test

*** Keywords ***
Setup Test
    tmsh create ltm virtual lacp-test2 destination 198.18.32.2:80 mask 255.255.255.255 ip-protocol tcp pool http_test_pool
    tmsh create ltm virtual lacp-test3 destination 198.18.32.3:80 mask 255.255.255.255 ip-protocol tcp pool http_test_pool
    tmsh create ltm virtual lacp-test4 destination 198.18.32.4:80 mask 255.255.255.255 ip-protocol tcp pool http_test_pool
    tmsh modify ltm virtual-address 198.18.32.2 route-advertisement selective
    tmsh modify ltm virtual-address 198.18.32.3 route-advertisement selective
    tmsh modify ltm virtual-address 198.18.32.4 route-advertisement selective
    Start Ixia Test     lacp.rxf
    tmsh reset net interface
    Sleep               1
    Get interface stats 2.1
    Get interface stats 2.2
    Sleep               120

Teardown Test
    Stop Ixia Test
    tmsh delete ltm virtual lacp-test2
    tmsh delete ltm virtual lacp-test3
    tmsh delete ltm virtual lacp-test4