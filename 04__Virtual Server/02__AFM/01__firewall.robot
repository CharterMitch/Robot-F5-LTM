*** Settings ***
Resource        ../../common.resource
Library         ../../F5Rest.py  ${f5_primary}     ${user}
Variables       ../settings.yaml
Library         String

*** Variables ***
# These clients are configured in the IXIA test source.
# They are used to validate the AFM rules.
${ixia_fqdntest1}       198.18.0.11
${ixia_fqdntest2}       198.18.0.12
${v6_ixia_fqdntest1}    2001:200:0:1100::11
${v6_ixia_fqdntest2}    2001:200:0:1100::12

*** Keywords ***
Build Ixia Chart
    [Documentation]     Gather IXIA test stats for the currently running test
    ...                 then return an HTML graph.
    ${stats}=           Gather IXLoad Stats
    @{graph}=           Create List     HTTP Concurrent Connections    HTTP Simulated Users    HTTP Requests Failed
    ${chart}=           IXLoad Chart ${stats} ${graph}
    [Return]            ${chart}

DNS Entry Exists
    [Documentation]             Refresh FQDN entries and make sure a value was returned from DNS server.
    [Arguments]                 ${fqdn}
    tmsh load security firewall fqdn-entity all
    Sleep                       3
    ${var}=                     tmsh show security firewall fqdn-info fqdn ${fqdn}
    Should not match regexp     ${var}  IP Addresses.+-\n

Resolve V4 DNS Entries
    [Documentation]                 DNS entries can be loaded into the AFM module.
    # Wait                          Wait for    Retry every     Commmand
    Wait until keyword succeeds     5 min       5 sec           DNS Entry Exists    fqdntest1.qa.com
    Wait until keyword succeeds     5 min       5 sec           DNS Entry Exists    fqdntest2.qa.com
    ${fqdntest1}=                   tmsh show security firewall fqdn-info fqdn fqdntest1.qa.com
    ${fqdntest2}=                   tmsh show security firewall fqdn-info fqdn fqdntest2.qa.com
    Should contain                  ${fqdntest1}    ${ixia_fqdntest1}
    Should contain                  ${fqdntest2}    ${ixia_fqdntest2}

Resolve V6 DNS Entries
    [Documentation]                 DNS entries can be loaded into the AFM module.
    # Wait                          Wait for    Retry every     Commmand
    Wait until keyword succeeds     2 min       5 sec           DNS Entry Exists    fqdntest1.qa.com
    Wait until keyword succeeds     2 min       5 sec           DNS Entry Exists    fqdntest2.qa.com
    ${fqdntest1}=                   tmsh show security firewall fqdn-info fqdn fqdntest1.qa.com
    ${fqdntest2}=                   tmsh show security firewall fqdn-info fqdn fqdntest2.qa.com
    Should contain                  ${fqdntest1}    ${v6_ixia_fqdntest1}
    Should contain                  ${fqdntest2}    ${v6_ixia_fqdntest1}

Setup AFM for V6
    # Change dns resolver to V6
    tmsh modify net dns-resolver lab-dns { forward-zones replace-all-with { qa.com { nameservers replace-all-with { ${v6_dns_server_1}.domain { } ${v6_dns_server_2}.domain { } } } } randomize-query-name-case no route-domain 0 use-tcp no }
    Start Ixia Test                 fqdn_fw_ipv6.rxf
    # Wait                          Wait for    Retry every     Commmand
    Wait until keyword succeeds     1 min       5 sec           Resolve V6 DNS Entries


*** Test Cases ***
IPV4 FQDN Firewall
    [Documentation]             Connections to virtual servers are blocked
    ...                         or allowed using FQDN entries.
    [Setup]                     Start Ixia Test     fqdn_fw_ipv4.rxf
    Resolve V4 DNS Entries
    # How can we timeout the Build IXIA Chart so we can collect stats for 5 minutes, etc.?
    #${chart}=                  Build Ixia Chart
    #Log                        ${chart}    HTML
    Sleep                       200
    ${rule_stat}                tmsh show security firewall rule-stat
    ${virtual_server}           Get Lines Matching regexp    ${rule_stat}   virtual +${virtual_server}  partial_match=true
    ${allow}                    Get Lines Containing String  ${virtual_server}   allow
    ${block}                    Get Lines Containing String  ${virtual_server}   block
    # Verify allow and block counters are not 0
    Should not match regexp     ${allow}  enforced +0
    Should not match regexp     ${block}  enforced +0
    # Verify allow and block counters are in the thousands of hits
    Should match regexp         ${allow}  enforced.+K
    Should match regexp         ${block}  enforced.+K
    # TODO: Compare number of allowed vs number of blocked connections - they should be relatively equal.
    [Teardown]                  Stop Ixia Test

IPV6 FQDN Firewall
    [Documentation]             Connections to virtual servers are blocked
    ...                         or allowed using FQDN entries.
    [Setup]                     Setup AFM for V6
    # How can we timeout the Build IXIA Chart so we can collect stats for 5 minutes, etc.?
    #${chart}=                  Build Ixia Chart
    #Log                        ${chart}    HTML
    Sleep                       600
    ${rule_stat}                tmsh show security firewall rule-stat
    ${virtual_server}           Get Lines Matching regexp    ${rule_stat}   virtual +${v6_virtual_server}  partial_match=true
    ${allow}                    Get Lines Containing String  ${virtual_server}   allow
    ${block}                    Get Lines Containing String  ${virtual_server}   block
    # Verify allow and block counters are not 0
    Should not match regexp     ${allow}  enforced +0
    Should not match regexp     ${block}  enforced +0
    # Verify allow and block counters are in the thousands of hits
    Should match regexp         ${allow}  enforced.+K
    Should match regexp         ${block}  enforced.+K
    # TODO: Compare number of allowed vs number of blocked connections - they should be relatively equal.
    [Teardown]                  Stop Ixia Test