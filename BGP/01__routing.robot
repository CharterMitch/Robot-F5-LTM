*** Settings ***
# https://clouddocs.f5.com/api/icontrol-soap/LocalLB__LBMethod.html
Resource    ../common.resource
Variables   settings.yaml
Library     ../F5Rest.py  ${f5_a}   ${user}

*** Variables ***
# What variables should we declare directly in the test?
${kernel_route}     198.18.32.1

*** Test Cases ***
Neighbors Established
    [Documentation]     Verify BGP neighbors.
    ${result}           zebos -c 'show bgp neighbors'
    Should contain      ${result}    Established
    Should not contain  ${result}    Active
    Log                 ${result}   

Kernel route advertisement
    [Documentation]     Advertise a kernel route to an upstream peer.
    ${result}           zebos -c 'show bgp neighbors'
    Log     test


Prefix list
    [Documentation]     Test that a v4 prefix list blocks an advertisement.
    Log     test2