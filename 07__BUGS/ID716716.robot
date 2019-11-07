*** Settings ***
Resource    ../common.resource
Library     ../F5Rest.py  ${f5_primary}     ${user}
#
# https://cdn.f5.com/product/bugtracker/ID716716.html
#
# Steps to Reproduce:
#   - Create a setup similar to the following:
#   -- Two networks connected by a router.
#   -- A BIG-IP connected to one of the networks.
#   -- A server connected to the other network.
#   - Create a pool with an ipip profile and a monitor (we used an http monitor).
#   -- Add the server to this pool as a member.
#   - Configure a gateway route on the BIG-IP, like this:
#
#   net route internal2 {
#        gw 10.2.1.10
#        network 10.2.129.0/24
#    }
#  The BIG-IP can talk to the server through the router.
#
#- Once you have verified all is connected and the monitor is working as expected
# then remove the BIG-IP route and replace it with a kernel route.
#
# tmsh delete net route internal2
# ip route add 10.2.129.0/24 via 10.2.1.10
#
# - Wait until the monitor queries the server.
#
#   Actual Results:
#    - TMM will core and restart.
#
#   Expected Results:
#   - TMM should not core.
#
*** Variables ***
${pool}         id716716
${server}       198.18.0.10
${network}      198.18.0.0/19
${gateway}      198.18.96.2

*** Keywords ***
Setup Bug
    tmsh create ltm node ${server} address ${server}
    tmsh create ltm pool ${pool} { members add { ${server}:80 } monitor http }
    tmsh create net route internal gw ${gateway} network ${network}
    imish -c 'ip route ${network} ${gateway}'
    Sleep   30
    tmsh delete net route internal

Teardown
    imish -c 'no ip route ${network} ${gateway}'
    tmsh delete ltm pool ${pool}
    tmsh delete ltm node ${server}

*** Test Cases ***
ID716716
    [Documentation]     Bug ID 716716: Under certain circumstances having a kernel
    ...                 route but no TMM route can lead to a TMM core.
    [Setup]             Setup Bug
    Sleep               35
    # Make sure there are no core dump files
    ${var}              bash ls -l /var/core/
    Should Match        ${var}   total 0\\n
    [Teardown]          Teardown
