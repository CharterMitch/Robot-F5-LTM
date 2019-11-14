*** Settings ***
Resource    ../common.resource
Library     ../F5Rest.py  ${f5_primary}     ${user}
Variables   settings.yaml

*** Keywords ***
Build Ixia Chart
    [Documentation]     Gather IXIA test stats for the currently running test
    ...                 then return an HTML graph.
    ${stats}=           Gather IXLoad Stats
    @{graph}=           Create List     HTTP Concurrent Connections    HTTP Simulated Users    HTTP Requests Failed
    ${chart}=           IXLoad Chart ${stats} ${graph}
    [Return]            ${chart}

*** Test Cases ***
Resolve DNS Entry
    [Documentation]         DNS entries are loaded into the AFM module.
    [Setup]                 tmsh load security firewall fqdn-entity all
    ${fqdntest1}=           tmsh show security firewall fqdn-info fqdn fqdntest1.qa.com
    Log                     ${fqdntest1}

Block connections using FQDN
    [Documentation]         Connections to virtual server are blocked or allowed
    ...                     using FQDN entries.
    [Setup]                 Start Ixia Test     v4_http.rxf
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
