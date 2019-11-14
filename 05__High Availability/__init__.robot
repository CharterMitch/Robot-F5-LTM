*** Settings ***
Documentation    High Availability Testing
Resource        ../common.resource
Variables       settings.yaml
Library         ../F5Rest.py  ${f5_primary}     ${user}     WITH NAME  primary
Library         ../F5Rest.py  ${f5_secondary}   ${user}     WITH NAME  secondary
Suite Setup     Configure F5
Suite Teardown  Teardown

*** Keywords ***
Configure F5
    [Documentation]     Setup the F5 for HA testing.
    [tags]              Setup
    primary.tmsh modify /cm device bigip1 configsync-ip ${primary_config_sync}
    primary.tmsh modify /cm device bigip1 unicast-address {{ ip ${primary_config_sync} }}
    secondary.tmsh modify /cm device ${f5_secondary}[name] configsync-ip ${secondary_config_sync}
    secondary.tmsh modify /cm device ${f5_secondary}[name] unicast-address {{ ip ${secondary_config_sync} }}
    primary.tmsh modify /cm trust-domain /Common/Root add-device { device-ip ${f5_secondary}[host] device-name ${f5_secondary}[name] username ${user}[username] password ${user}[password] }
    primary.tmsh create /cm device-group SyncFailover devices add { bigip1 ${f5_secondary}[name] } type sync-failover save-on-auto-sync true auto-sync enabled
    primary.tmsh modify cm traffic-group traffic-group-1 ha-order { bigip1 ${f5_secondary}[name] } auto-failback-enabled true
    primary.tmsh run /cm config-sync force-full-load-push to-group SyncFailover
    primary.tmsh save /sys config
    secondary.tmsh save /sys config

Teardown
    [Documentation]     Teardown the configuration for this test suite.
    [tags]              Teardown
    # Is there a reason to teardown the HA config?
    No Operation