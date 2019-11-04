*** Settings ***
# https://clouddocs.f5.com/api/icontrol-soap/LocalLB__LBMethod.html
Resource    ../common.resource
Variables   settings.yaml
Library     ../F5Rest.py  ${f5_primary}   ${user}

*** Test Cases ***
V4 Route Health Injection
    No Operation

V6 Route Health Injection
    No Operation



