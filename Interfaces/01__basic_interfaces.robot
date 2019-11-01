*** Settings ***
# https://clouddocs.f5.com/api/icontrol-soap/LocalLB__LBMethod.html
Resource    ../common.resource
Variables   settings.yaml
Library     ../F5Rest.py  ${f5_a}   ${user}

*** Test Cases ***
Interface Speed and Duplex
    [Documentation]
    No Operation

Interface Trunk
    [Documentation]
    No Operation

Disable Interface
    [Documentation]
    No Operation

Enable Interface
    [Documentation]
    No Operation