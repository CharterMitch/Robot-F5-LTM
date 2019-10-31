*** Settings ***
# https://clouddocs.f5.com/api/icontrol-soap/LocalLB__LBMethod.html
Resource    ../common.resource
Variables   settings.yaml

*** Test Cases ***
Round Robin
    [Documentation]     Connections are distributed evenly across all 
    ...                 members in the pool.
    Sleep   30
    # Gather traffic statistics
    &{total_connections}=   Get total connections from pool ${pool}
    ${c1}   Set variable    &{total_connections}[${node_1}] 
    ${c2}   Set variable    &{total_connections}[${node_2}]
    ${diff}=    Percent difference between ${c1} and ${c2}
    # Each node should have more than 0 connections
    Should be true  ${c1}>0
    Should be true  ${c2}>0
    # Difference between pool members should be less than 1%
    Should be true  ${diff}<1
    Log     Round Robin connection difference is ${diff}

Member Ratio
    [Documentation]     Connections are sent to a member with a high ratio 
    ...                 number more often than a member with a lower ratio 
    ...                 number.
    Set pool ${pool} method LB_METHOD_RATIO_MEMBER
    # Set the ratio of the first member to 10 and the second member to 1
    Set pool ratio   ${pool}    10      1
    Reset pool statistics   ${pool}
    Sleep   30
    # Gather traffic statistics
    &{total_connections}=   Get total connections from pool ${pool}
    ${c1}   Set variable    &{total_connections}[${node_1}] 
    ${c2}   Set variable    &{total_connections}[${node_2}]
    ${diff}=    Percent difference between ${c1} and ${c2}
    # Each node should have more than 0 connections
    Should be true  ${c1}>0
    Should be true  ${c2}>0
    # Node 1 should have more connections than node 2 (~10x more)
    Should be true  ${c1}>${c2}
    # Difference between pool members greater than 80%
    Should be true  ${diff}>80
    Log     Member ratio connection difference is ${diff}

Fastest App Response
    # Can the IXIA setup two HTTP server and add 100ms of delay to the second?
    Log     Not implemented.