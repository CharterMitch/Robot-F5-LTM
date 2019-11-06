# Common keywords for Load Balancing tests
*** Keywords ***
Reset Statistics
    [Documentation]     Reset various statistics on the F5.
    ${test} =   tmsh reset-stats ltm virtual
    tmsh reset-stats ltm pool
    tmsh reset-stats ltm profile client-ssl clientssl

Log F5 Statistics
    [Documentation]     Log statistics.
    ${v1}=  tmsh show ltm pool
    ${v2}=  tmsh show ltm virtual
    ${v3}=  tmsh show ltm profile client-ssl clientssl | grep -i Protocol
    Log Many    ${v1}   ${v2}   ${v3}