*** Settings ***
Resource    ../common.resource
Variables   settings.yaml

*** Test Cases ***
#SSL Offload
#    [Documentation]     The F5 performs SSL offloading to HTTP servers.
    # Start IXIA SSL Test
    #Sleep   120
    # Build virtual server for HTTPS offload
    # How do we validate this?
