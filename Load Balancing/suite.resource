# Common keywords for Load Balancing tests
*** Keywords ***
Reset Statistics
    [Documentation]     Reset various statistics on the F5.
    ${test} =   tmsh reset-stats ltm virtual
    tmsh reset-stats ltm pool
    tmsh reset-stats ltm profile client-ssl clientssl

Log F5 Statistics
    [Documentation]     Log virtual server, pool, member and profile statistics.
    [Arguments]         ${pool}     ${virtual_server}
    ${show_ltm_pool}=           tmsh show ltm pool ${pool}
    ${show_ltm_pool_members}=   tmsh show ltm pool ${pool} members
    ${show_ltm_virtual}=        tmsh show ltm virtual ${virtual_server}
    ${show_ltm_profile}=        tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    Log     ${show_ltm_pool}
    Log     ${show_ltm_pool_members}
    Log     ${show_ltm_virtual}
    Log     ${show_ltm_profile}