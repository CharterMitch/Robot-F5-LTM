*** Settings ***
Documentation    Advanced Firewall Manager (AFM) Tests
Resource        ../common.resource
Library         ../F5Rest.py    ${f5_primary}     ${user}
Suite Setup     Setup AFM
Suite Teardown  Teardown

*** Variables ***
${test_domain}      qa.com
${dns_server_1}     198.18.64.11
${dns_server_2}     198.18.64.12

*** Keywords ***
Setup AFM
    [Documentation]     Setup nodes, pools and virtual servers to use
    ...                 in Load Balancing test cases.
    ...                 Variables are from the settings.yaml file in this folder.
    [tags]              Setup
    # Add DNS resolver for AFM
    tmsh create net dns-resolver lab-dns { forward-zones replace-all-with { ${test_domain} { nameservers replace-all-with { ${dns_server_1}:domain { } ${dns_server_2}:domain { } } } } route-domain 0 use-tcp no }
    tmsh modify security firewall global-fqdn-policy { dns-resolver lab-dns }
    # Add FQDN entities for testing
    tmsh create security firewall fqdn-entity fqdntest1.qa.com { }
    tmsh create security firewall fqdn-entity fqdntest2.qa.com { }
    tmsh create security firewall fqdn-entity fqdntest3.qa.com { }
    # Firewall rule
    tmsh create security firewall policy FQDN_Policy1 rules add { Test1 { action accept place-before first destination { fqdns replace-all-with { fqdntest1.qa.com }}}}
    tmsh create security firewall policy FQDN_Policy1 rules add { Test2 { action accept place-before first destination { fqdns replace-all-with { fqdntest2.qa.com }}}}
    tmsh create security firewall policy FQDN_Policy1 rules add { Test3 { action rject place-before first destination { fqdns replace-all-with { fqdntest3.qa.com }}}}
    # Apply firewall rules to virtual servers
    tmsh modify ltm virtual SPOCSLBTestbedEnv1-VirtualServer-1 fw-enforced-policy FQDN_Policy1
    tmsh modify ltm virtual SPOCSLBTestbedEnv1-VirtualServer-1-https fw-enforced-policy FQDN_Policy1
    tmsh modify ltm virtual SPOCSLBTestbedEnv1-VirtualServer-2 fw-enforced-policy FQDN_Policy1
    tmsh modify ltm virtual SPOCSLBTestbedEnv1-VirtualServer-2-https fw-enforced-policy FQDN_Policy1


Teardown
    tmsh modify security firewall global-fqdn-policy { dns-resolver none }
    tmsh delete security firewall policy FQDN_Policy1