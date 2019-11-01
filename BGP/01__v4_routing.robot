*** Settings ***
# https://clouddocs.f5.com/api/icontrol-soap/LocalLB__LBMethod.html
Resource    ../common.resource
Variables   settings.yaml
Library     ../F5Rest.py  ${f5_a}   ${user}

*** Variables ***
# What variables should we declare directly in the test?
${kernel_route}     198.18.32.1

*** Test Cases ***
IPv4 Neighbors Established
    [Documentation]     Verify IPv4 BGP neighbors.
    ${result}     zebos -c 'show bgp neighbors 198.18.96.1 | grep state'
    Log                 ${result}
    Should contain      ${result}    Established
    Should not contain  ${result}    Active

IPv6 Neighbors Established
    [Documentation]     Verify IPv6 BGP neighbors.
    ${result}     zebos -c 'show bgp summary'
    Log     ${result}

Kernel route advertisement
    [Documentation]     Advertise a kernel route to an upstream peer.
    Log     test


Prefix list
    [Documentation]     Test that a v4 prefix list blocks an advertisement.
    Log     test2