*** Settings ***
Resource        ../common.resource
Library         ../F5Rest.py  ${f5_primary}     ${user}
Suite Setup     tmsh modify sys ntp servers replace-all-with { 10.240.72.125 } timezone America/Denver

*** Test Cases ***
NTP Daemon is Running
    [Documentation]         NTP daemon is running.
    ${ntpd}=                tmsh show /sys service ntpd
    Should Match Regexp     ${ntpd}     running...

NTP Polling
    [Documentation]         The value of 377 in the reach column indicates that 
    ...                     the server was successfully reached during each of 
    ...                     the last eight attempts.
    ...                     https://support.f5.com/csp/article/K10240
    ${ntp}=                 bash ntpq -np
    Should Match Regexp     ${ntp}    377