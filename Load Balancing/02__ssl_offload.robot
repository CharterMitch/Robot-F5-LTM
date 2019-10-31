*** Settings ***
Resource    ../common.resource
Variables   settings.yaml

*** Variables ***
# These variables must match the variables in __init__.robot
${pool}     http_test_pool
${node_1}   198.18.64.11
${node_2}   198.18.64.12

*** Test Cases ***
#SSL Offload
#    [Documentation]     The F5 performs SSL offloading to HTTP servers.
    # Start IXIA SSL Test
    #Sleep   120
    # Build virtual server for HTTPS offload
    # How do we validate this?
