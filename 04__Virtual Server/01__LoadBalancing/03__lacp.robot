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
    Sleep               120
    Stop Ixia Test
    ${int_1}=     Get interface stats 2.1
    ${int_2}=     Get interface stats 2.2
    ${diff_in}=         Percentage difference ${int_1.counters_pktsIn.value} ${int_2.counters_pktsIn.value}
    ${diff_out}=        Percentage difference ${int_1.counters_pktsOut.value} ${int_2.counters_pktsOut.value}
    # Allow 5% difference between interfaces
    Should be true      ${diff_in}<5
    Should be true      ${diff_out}<5
    [Teardown]          Teardown Test

*** Keywords ***
Setup Test
    tmsh create ltm virtual LACP-TEST destination ${network}:any mask ${mask} ip-forward
    tmsh create ltm nat LACP-NAT { originating-address 198.18.64.0 traffic-group traffic-group-1 translation-address ${network} }
    imish -c 'enable','conf t','ip route ${cidr} null'
    Start Ixia Test     lacp.rxf
    tmsh reset net interface
    Get interface stats 2.1
    Get interface stats 2.2

Teardown Test
    tmsh delete ltm virtual LACP-TEST
    tmsh delete ltm nat LACP-NAT
    imish -c 'enable','conf t','no ip route ${cidr} null'
