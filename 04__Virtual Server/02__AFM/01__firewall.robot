*** Settings ***
Resource        ../../common.resource
Library         ../../F5Rest.py  ${f5_primary}     ${user}
Variables       ../settings.yaml
#Suite Setup     Start Ixia Test     fqdn_fw_ipv4.rxf

*** Keywords ***
Build Ixia Chart
    [Documentation]     Gather IXIA test stats for the currently running test
    ...                 then return an HTML graph.
    ${stats}=           Gather IXLoad Stats
    @{graph}=           Create List     HTTP Concurrent Connections    HTTP Simulated Users    HTTP Requests Failed
    ${chart}=           IXLoad Chart ${stats} ${graph}
    [Return]            ${chart}

*** Keywords ***
DNS Entry Exists
    [Documentation]     Refresh FQDN entries and make sure a value was returned from DNS server.
    [Arguments]         ${fqdn}
    tmsh load security firewall fqdn-entity all
    ${var}=             tmsh show security firewall fqdn-info fqdn ${fqdn}
    Should not match regexp     ${var}  IP Addresses:.+-\n

*** Test Cases ***
Resolve DNS Entry
    [Documentation]         DNS entries are loaded into the AFM module.
    # Wait                          Wait for    Retry every     Commmand
    Wait until keyword succeeds     1 min       5 sec           DNS Entry Exists    fqdntest1.qa.com
    tmsh show security firewall fqdn-info fqdn fqdntest1.qa.com

IPV4 FQDN Firewall
    [Documentation]         Connections to virtual server are blocked or allowed
    ...                     using FQDN entries.
    # How can we timeout the Build IXIA Chart so we can collect stats for 5 minutes, etc.?
    #${chart}=               Build Ixia Chart
    #Log                     ${chart}    HTML
    tmsh show security firewall rule-stat
    [Teardown]              Stop Ixia Test


