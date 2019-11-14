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
    ${interfaces}=      bash tmsh show net interface all-properties \| sed -r "s\/[ ]+\/\|\/g" \| grep Uplink \| cut -d"\|" -f 5,6,20
    ${interface_1}=     Get Line    ${interfaces}   0
    ${interface_2}=     Get Line    ${interfaces}   1
    Should be Equal     ${interface_1}      ${interface_2}
    [Teardown]          Teardown Test

*** Keywords ***
Setup Test
    tmsh create ltm virtual LACP-TEST destination ${network}:any mask ${mask} ip-forward
    tmsh create ltm nat LACP-NAT { originating-address 198.18.64.0 traffic-group traffic-group-1 translation-address ${network} }
    imish -c 'enable','conf t','ip route ${cidr} null'
    Start Ixia Test     lacp.rxf
    tmsh reset net interface

Teardown Test
    tmsh delete ltm virtual LACP-TEST
    tmsh delete ltm nat LACP-NAT
    imish -c 'enable','conf t','no ip route ${cidr} null'
