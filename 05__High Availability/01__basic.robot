*** Settings ***
Resource        ../common.resource
Library         ../F5Rest.py  ${f5_primary}     ${user}     WITH NAME  primary
Library         ../F5Rest.py  ${f5_secondary}   ${user}     WITH NAME  secondary

*** Test Cases ***
Primary device is Active
    ${primary}=             primary.tmsh show /cm failover-status
    Should match regexp     ${primary}  ACTIVE

Secondary device is Standby
    ${secondary}=           secondary.tmsh show /cm failover-status
    Should match regexp     ${secondary}  STANDBY

Manual failover
    [Setup]                 primary.tmsh run /sys failover standby
    Sleep                   10
    ${primary}=             primary.tmsh show /cm failover-status
    Should match regexp     ${primary}      STANDBY
    ${secondary}=           secondary.tmsh show /cm failover-status
    Should match regexp     ${secondary}    ACTIVE
    [Teardown]              secondary.tmsh run /sys failover standby
