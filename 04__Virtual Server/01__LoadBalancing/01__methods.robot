*** Settings ***
Resource    ../../common.resource
Library     ../../F5Rest.py  ${f5_primary}     ${user}
Variables   ../settings.yaml

*** Keywords ***
Build Ixia Chart
    [Documentation]     Gather IXIA test stats for the currently running test
    ...                 then return an HTML graph.
    ${stats}=           Gather IXLoad Stats
    @{graph}=           Create List     HTTP Concurrent Connections    HTTP Simulated Users    HTTP Requests Failed
    ${chart}=           IXLoad Chart ${stats} ${graph}
    [Return]            ${chart}

Reset Statistics
    [Documentation]     Reset various statistics on the F5.
    ${test}=            tmsh reset-stats ltm virtual
    tmsh reset-stats ltm pool
    tmsh reset-stats ltm profile client-ssl clientssl

Log F5 Pool Data
    [Documentation]     Log virtual server, pool, member and profile statistics.
    [Arguments]         ${pool}     ${virtual_server}
    tmsh show ltm pool ${pool}
    tmsh show ltm pool ${pool} members
    tmsh show ltm virtual ${virtual_server}
    tmsh show ltm profile client-ssl clientssl | grep -i Protocol

*** Test Cases ***
Round Robin
    [Documentation]         Connections are distributed evenly across all 
    ...                     members in the pool.
    [Setup]                 Start Ixia Test     v4_http.rxf
    tmsh reset-stats ltm pool
    tmsh modify ltm pool ${pool} load-balancing-mode round-robin
    ${chart}=               Build Ixia Chart
    Log                     ${chart}    HTML
    # You can find the "Get stats for pool" keyword in F5Rest.py
    &{stats}=               Get stats for pool ${pool}
    # Can use "Get from dictionary" keyword to make this less cryptic?
    ${pool_member_1}        Set variable    ${stats['/Common/${node_1}']['serverside_totConns']['value']}
    ${pool_member_2}        Set variable    ${stats['/Common/${node_2}']['serverside_totConns']['value']}
    ${diff}=                Percentage difference ${pool_member_1} ${pool_member_2}
    # Difference between pool member connections should be less than 1% for round-robin
    Should be true          ${diff}<1
    Should be true          ${pool_member_1}>0
    Should be true          ${pool_member_2}>0
    Log                     Round Robin connection difference is ${diff}
    Log F5 Pool Data        ${pool}     ${virtual_server}
    [Teardown]              Stop Ixia Test

Member Ratio
    [Documentation]         Connections are sent to a member with a high ratio 
    ...                     number more often than a member with a lower ratio 
    ...                     number.
    [Setup]                 Start Ixia Test     v4_http.rxf
    tmsh modify ltm pool ${pool} load-balancing-mode ratio-member
    tmsh modify ltm pool http_test_pool {members modify {${node_1}:http { ratio 10 }}}
    tmsh reset-stats ltm pool
    ${chart}=               Build Ixia Chart
    Log                     ${chart}    HTML
    &{stats}=               Get stats for pool ${pool}
    ${pool_member_1}        Set variable    ${stats['/Common/${node_1}']['serverside_totConns']['value']}
    ${pool_member_2}        Set variable    ${stats['/Common/${node_2}']['serverside_totConns']['value']}
    ${diff}=                Percentage difference ${pool_member_1} ${pool_member_2}
    # Node 1 should have more connections than node 2 (~10x more)
    Should be true          ${pool_member_1}>${pool_member_2}
    # Difference between pool members greater than 80%
    Should be true          ${diff}>80
    Should be true          ${pool_member_1}>0
    Should be true          ${pool_member_2}>0
    Log     Member ratio connection difference is ${diff}
    Log F5 Pool Data        ${pool}     ${virtual_server}
    [Teardown]              Stop Ixia Test

Least Connections Node
    [Documentation]         This method is used in production.
    No Operation
