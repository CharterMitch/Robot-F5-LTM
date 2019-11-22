*** Settings ***
Resource    ../../common.resource
Library     ../../F5Rest.py  ${f5_primary}     ${user}
Variables   ../settings.yaml

*** Keywords ***
IXIA Stats as Pandas df
    [Documentation]     Gather IXIA test stats for the currently running test
    ...                 then return the data as a pandas dataframe (df).
    ${stats}=           Gather IXLoad Stats
    ${df}=              Convert to dataframe ${stats}
    [Return]            ${df}

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
    [Setup]                 Run Keywords    Start Ixia Test     v4_http.rxf
    ...                     AND             tmsh reset-stats ltm pool
    ...                     AND             tmsh modify ltm pool ${pool} load-balancing-mode round-robin
    ${df}=                  IXIA Stats as Pandas df
    @{cols}=                Create List     HTTP Concurrent Connections    HTTP Simulated Users    HTTP Requests Failed
    HTML Chart              ${df}   ${cols}
    Should be true          ${df['HTTP Concurrent Connections'].mean()}>400
    Should be true          ${df['HTTP Requests Failed'].sum()}==0
    &{stats}=               Get stats for pool ${pool}
    # Total connections for each pool member
    ${pool_member_1}        Set variable    ${stats['/Common/${node_1}']['serverside_totConns']['value']}
    Should be true          ${pool_member_1}>0
    ${pool_member_2}        Set variable    ${stats['/Common/${node_2}']['serverside_totConns']['value']}
    Should be true          ${pool_member_2}>0
    # Difference between pool member connections should be less than 1% for round-robin
    ${diff}=                Percentage difference ${pool_member_1} ${pool_member_2}
    Should be true          ${diff}<1
    [Teardown]              Run Keywords    Stop Ixia Test
    ...                     AND             Log F5 Pool Data    ${pool}     ${virtual_server}

Member Ratio
    [Documentation]         Connections are sent to a member with a high ratio 
    ...                     number more often than a member with a lower ratio 
    ...                     number.
    [Setup]                 Run Keywords  Start Ixia Test     v4_http.rxf
    ...                     AND     tmsh modify ltm pool ${pool} load-balancing-mode ratio-member
    ...                     AND     tmsh modify ltm pool http_test_pool {members modify {${node_1}:http { ratio 10 }}}
    ...                     AND     tmsh reset-stats ltm pool
    ${df}                   IXIA Stats as Pandas df
    @{cols}=                Create List     HTTP Concurrent Connections    HTTP Simulated Users    HTTP Requests Failed
    HTML chart              ${df}   ${cols}
    Should be true          ${df['HTTP Requests Failed'].sum()}==0
    &{stats}=               Get stats for pool ${pool}
    ${pool_member_1}        Set variable    ${stats['/Common/${node_1}']['serverside_totConns']['value']}
    Should be true          ${pool_member_1}>0
    ${pool_member_2}        Set variable    ${stats['/Common/${node_2}']['serverside_totConns']['value']}
    Should be true          ${pool_member_2}>0
    ${diff}=                Percentage difference ${pool_member_1} ${pool_member_2}
    # Node 1 should have more connections than node 2 (~10x more)
    Should be true          ${pool_member_1}>${pool_member_2}
    # Difference between pool members greater than 80%
    Should be true          ${diff}>80
    Log F5 Pool Data        ${pool}     ${virtual_server}
    [Teardown]              Run Keywords    Stop Ixia Test
    ...                     AND             Log F5 Pool Data    ${pool}     ${virtual_server}

Least Connections Node
    [Documentation]         This method is used in production.
    No Operation
