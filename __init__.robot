*** Settings ***
Documentation   F5 New Code Validation
Resource        common.resource
Library         F5Rest.py  ${f5_primary}     ${user}     WITH NAME  primary
Library         F5Rest.py  ${f5_secondary}   ${user}     WITH NAME  secondary
Suite Setup     Setup lab
#Suite Teardown  Teardown lab

*** Variables ***
${primary_config_file}      f5_primary.tmsh
${secondary_config_file}    f5_secondary.tmsh
${imish_config_file}        imish.config

*** Keywords ***
Setup lab
    [Documentation]     Configure the lab topology for all of the test cases.
    ...                 This requires the F5s to be previously licensed.
    Run Keyword If  '${default_config}'=='True'     Default configurations
    Run Keyword If  '${send_base_config}'=='True'   Load Base Config
    Run Keyword If  '${send_imish_config}'=='True'  Load imish Config
    #Setup Polatis

Load Base Config
    [Documentation]     Configure the F5 physical devices, links, ip addresses.
    [tags]              Setup
    # Default device configurations if settings.yaml is set to True
    Log     Sending TMSH commands to configure F5s  WARN
    # Load base config tmsh commands from local file
    primary.load tmsh ${primary_config_file}
    primary.tmsh save /sys config
    secondary.load tmsh ${secondary_config_file}
    secondary.tmsh save /sys config

Load imish Config  
    [Documentation]     Load ZebOS configuration from a local file.
    Log     Send imish commands from ${imish_config_file}    WARN
    primary.load imish ${imish_config_file}
    secondary.load imish ${imish_config_file}

Setup Polatis
    [Documentation]     Configure the Polatis optical switch to configure 
    ...                 cross-connects properly for our lab ports.
    [tags]              Setup
    # Connect IXIA 11/1 to the nxs05sqsccc 4/2 port
    Cross-connect polatis port 1 to 323
    Cross-connect polatis port 193 to 131
    # Connect IXIA 11/2 to the nxs05sqsccc 4/1 port
    Cross-connect polatis port 4 to 324
    Cross-connect polatis port 196 to 132

Default Configurations
    [Documentation]     Default the F5 configurations to factory default.
    Log  Defaulting F5 Configurations!   WARN
    primary.tmsh load /sys config default
    Sleep   15
    secondary.tmsh load /sys config default
    Sleep   15

Teardown Lab
    [Documentation]     Teardown lab.
    #primary.tmsh load /sys config default
    #secondary.tmsh load /sys config default
    No Operation
    