*** Settings ***
Resource    ../common.resource
Library     ../F5Rest.py  ${f5_primary}     ${user}
Library     Dialogs
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
    # Log the software version of the F5
    ${sys}              tmsh show sys version
    Log                 ${sys}
    # Setup F5 for bug
    tmsh create ltm node ${server} address ${server}
    # Update below to add ipip profile
    tmsh create ltm pool ${pool} { members add { ${server}:80 } monitor http profiles add {ipip}}
    tmsh create net route internal gw ${gateway} network ${network}
    imish -c 'enable','conf t','ip route ${network} ${gateway}'
    # Start an IXIA test with a simple server to test aginst (198.18.0.10)
    Start Ixia Test     id716716.rxf
    # Wait                          Wait for    Retry every     Commmand
    Wait until keyword succeeds     30 sec      1 sec           Pool is available
    Log     Deleting kernel route, this should core TMM on next health check.     WARN
    tmsh delete net route internal

Teardown
    imish -c 'enable','conf t','no ip route ${network} ${gateway}'
    tmsh delete ltm pool ${pool}
    tmsh delete ltm node ${server}

Pool is available
    &{stats}=           Get stats for pool ${pool}
    ${status}           Set variable    ${stats['/Common/${server}']['monitorStatus']['description']}
    Should be equal     ${status}   up

*** Test Cases ***
ID716716
    [Documentation]     Bug ID 716716: Under certain circumstances having a kernel
    ...                 route but no TMM route can lead to a TMM core.
    ...                 https://cdn.f5.com/product/bugtracker/ID716716.html
    [Setup]             Setup Bug
    Sleep               30
    ${var}              bash grep tmrouted /var/log/ltm
    Log                 ${var}
    # If tmrouted connection closed is in the log file; tmm has cored
    Should Not Match Regexp      ${var}   tmrouted connection closed
    [Teardown]          Teardown
