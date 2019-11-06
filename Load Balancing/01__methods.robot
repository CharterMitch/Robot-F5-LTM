*** Settings ***
# https://clouddocs.f5.com/api/icontrol-soap/LocalLB__LBMethod.html
Resource    ../common.resource
Library     ../F5Rest.py  ${f5_primary}     ${user}
Variables   settings.yaml
Resource        suite.resource
Suite Setup     Start Ixia Test     v4_http.rxf
Suite Teardown  Stop Ixia Test

*** Test Cases ***
Round Robin
    [Documentation]     Connections are distributed evenly across all 
    ...                 members in the pool.
    # TODO: Start IXIA Test
    tmsh modify ltm pool ${pool} load-balancing-mode round-robin
    ${pool_info}=           Get pool ${pool}
    Should be equal         ${pool_info.loadBalancingMode}    round-robin
    tmsh reset-stats ltm pool
    # Wait a while for ixia test traffic
    Sleep   120
    &{stats}=               Get stats for pool ${pool}
    ${total_requests_1}     Set variable    ${stats['/Common/${node_1}']['serverside_totConns']['value']}
    ${total_requests_2}     Set variable    ${stats['/Common/${node_2}']['serverside_totConns']['value']}
    ${diff}=                Percentage difference ${total_requests_1} ${total_requests_2}
    # Difference between pool member connections should be less than 1% for round-robin
    Should be true          ${diff}<1
    Should be true          ${total_requests_1}>0
    Should be true          ${total_requests_2}>0
    Log                     Round Robin connection difference is ${diff}
    Log v4 Statistics

Member Ratio
    [Documentation]     Connections are sent to a member with a high ratio 
    ...                 number more often than a member with a lower ratio 
    ...                 number.
    tmsh modify ltm pool ${pool} load-balancing-mode ratio-member
    ${pool_info}=           Get pool ${pool}
    Should be equal         ${pool_info.loadBalancingMode}    ratio-member
    # Set the ratio of the first member to 10
    tmsh modify ltm pool http_test_pool {members modify {${node_1}:http { ratio 10 }}}
    tmsh reset-stats ltm pool
    # Wait a while for ixia test traffic
    Sleep   120
    # Gather traffic statistics
    &{stats}=               Get stats for pool ${pool}
    ${total_requests_1}     Set variable    ${stats['/Common/${node_1}']['serverside_totConns']['value']}
    ${total_requests_2}     Set variable    ${stats['/Common/${node_2}']['serverside_totConns']['value']}
    ${diff}=                Percentage difference ${total_requests_1} ${total_requests_2}
    # Node 1 should have more connections than node 2 (~10x more)
    Should be true          ${total_requests_1}>${total_requests_2}
    # Difference between pool members greater than 80%
    Should be true          ${diff}>80
    Should be true          ${total_requests_1}>0
    Should be true          ${total_requests_2}>0
    Log     Member ratio connection difference is ${diff}
    Log v4 Statistics

Fastest App Response
    # Can we setup two HTTP server traffic types and add 100ms of delay to the second?
    No Operation