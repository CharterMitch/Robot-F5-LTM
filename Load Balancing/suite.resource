# Common keywords for Load Balancing tests
*** Keywords ***
Reset Statistics
    [Documentation]     Reset various statistics on the F5.
    ${test} =   tmsh reset-stats ltm virtual
    tmsh reset-stats ltm pool
    tmsh reset-stats ltm profile client-ssl clientssl

Log v4 Statistics
    [Documentation]     Log statistics.
    ${v1}=  tmsh show ltm pool ${pool}
    ${v2}=  tmsh show ltm virtual ${virtual_server}
    ${v3}=  tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    Log Many    ${v1}   ${v2}   ${v3}

Log v6 Statistics
    [Documentation]     Log statistics.
    ${v1}=  tmsh show ltm pool ${v6_pool}
    ${v2}=  tmsh show ltm virtual ${v6_virtual_server}
    ${v3}=  tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    Log Many    ${v1}   ${v2}   ${v3}