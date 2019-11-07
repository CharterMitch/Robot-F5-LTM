*** Settings ***
Resource    ../common.resource
Variables   settings.yaml
Library     ../F5Rest.py  ${f5_primary}   ${user}

*** Test Cases ***
Neighbors Established
    [Documentation]     Verify BGP neighbors are all established.
    # Wait                          Wait for    Retry every     Commmand
    Wait until keyword succeeds     1 min       5 sec           Neighbors Established
    ${result}           imish -c 'show bgp neighbors'
    Log                 ${result}   

Shutdown V4 Neighbor
    [Documentation]     Verify neighbor shutdown command.
    [Setup]             imish -c 'enable','conf t','router bgp ${asn}','neighbor ${v4_peers}[0] shutdown'
    # Wait                          Wait for    Retry every     Commmand
    Wait until keyword succeeds     30 sec      2 sec           Neighbor Shutdown  ${v4_peers}[0]
    ${result}           imish -c 'show bgp neighbors ${v4_peers}[0]'
    Should contain      ${result}    Administratively shut down
    Should not contain  ${result}    Established
    Log                 ${result}

No Shutdown V4 Neighbor
    [Documentation]     Verify neighbor no shutdown command.
    [Setup]             imish -c 'enable','conf t','router bgp ${asn}','no neighbor ${v4_peers}[0] shutdown'
    # Wait                          Wait for    Retry every     Commmand
    Wait until keyword succeeds     30 sec      2 sec           Neighbor Established  ${v4_peers}[0] 
    ${result}           imish -c 'show bgp neighbors ${v4_peers}[0]'
    Log                 ${result} 

Shutdown V6 Neighbor
    [Documentation]     Verify neighbor shutdown command.
    [Setup]             imish -c 'enable','conf t','router bgp ${asn}','neighbor ${v6_peers}[0] shutdown'
    # Wait                          Wait for    Retry every     Commmand
    Wait until keyword succeeds     30 sec      2 sec           Neighbor Shutdown  ${v6_peers}[0]
    ${result}           imish -c 'show bgp neighbors ${v6_peers}[0]'
    Should contain      ${result}    Administratively shut down
    Should not contain  ${result}    Established
    Log                 ${result}

No Shutdown V6 Neighbor
    [Documentation]     Verify neighbor no shutdown command.
    [Setup]             imish -c 'enable','conf t','router bgp ${asn}','no neighbor ${v6_peers}[0] shutdown' 
    # Wait                          Wait for    Retry every     Commmand
    Wait until keyword succeeds     30 sec      2 sec           Neighbor Established  ${v6_peers}[0]
    ${result}           imish -c 'show bgp neighbors ${v6_peers}[0]'
    Log                 ${result}

*** Keywords ***
Neighbors Established
    [Documentation]     Verify all BGP neighbors are in the established state.
    ${result}           imish -c 'show bgp neighbors'
    Should contain      ${result}    Established
    Should not contain  ${result}    Active
    Should not contain  ${result}    Open
    Should not contain  ${result}    Idle

Neighbor Established
    [Documentation]     Verify a BGP neighbor is established.
    [Arguments]         ${neighbor}
    ${result}           imish -c 'show bgp neighbors ${neighbor}'
    Should contain      ${result}    Established

Neighbor Shutdown
    [Documentation]     Verify a BGP neighbor is shutdown (Idle).
    [Arguments]         ${neighbor}
    ${result}           imish -c 'show bgp neighbors ${neighbor}'
    Should contain      ${result}    Idle
