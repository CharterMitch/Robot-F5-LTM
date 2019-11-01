*** Settings ***
# https://clouddocs.f5.com/api/icontrol-soap/LocalLB__LBMethod.html
Resource    ../common.resource
Variables   settings.yaml

*** Variables ***
# What variables should we declare directly in the test?
${kernel_route}     198.18.32.1

*** Test Cases ***
Kernel route advertisement
    [Documentation]     Advertise a kernel route to an upstream peer.
    # Add kernel route ${kernel_route} or virtual server?
    # Verify kernel route?
    # show ip bgp ${kernel_route}

Prefix list
    [Documentation]     Test that a v4 prefix list blocks an advertisement.
    # Add kernel route {$kernel_route} or virtual server?
    # Verify route
    # show ip bgp ${kernel_route}