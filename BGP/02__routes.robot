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
    [Documentation]     Verify BGP neighbors are all established.
    Sleep               15
    ${result}           imish -c 'show bgp neighbors'
    Should contain      ${result}    Established
    Should not contain  ${result}    Active
    Should not contain  ${result}    Idle
    Log                 ${result}   

Shutdown Neighbor
    [Documentation]     Verify neighbor shutdown command.
    imish -c 'enable','conf t','router bgp 65279','neighbor 198.18.96.1 shutdown'
    Sleep               5
    ${result}           imish -c 'show bgp neighbors 198.18.96.1'
    Should contain      ${result}    Administratively shut down
    Should not contain  ${result}    Established
    Log                 ${result}

No Shutdown Neighbor
    [Documentation]     Verify no neighbor shutdown command.
    imish -c 'enable','conf t','router bgp 65279','no neighbor 198.18.96.1 shutdown' 
    Sleep               10
    ${result}           imish -c 'show bgp neighbors 198.18.96.1'
    Should contain      ${result}    Established
    Should not contain  ${result}    Idle
    Log                 ${result} 

Kernel route advertisement
    [Documentation]     Advertise a kernel route to an upstream peer.
    ${result}           imish -c 'show bgp neighbors'
    Log     test

Prefix list
    [Documentation]     Test that a v4 prefix list blocks an advertisement.
    Log     test2