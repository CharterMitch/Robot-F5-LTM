*** Settings ***
Resource        ../common.resource
Library         ../F5Rest.py  ${f5_primary}     ${user}
Suite Setup     tmsh modify /sys dns name-servers replace-all-with { 10.240.72.124 }

*** Test Cases ***
DNS Request
    [Documentation]         Dig charter.com
    ${dig}=                 bash dig charter.com
    Should Match Regexp     ${dig}  Got answer:
