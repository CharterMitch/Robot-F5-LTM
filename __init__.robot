*** Settings ***
Documentation   F5 New Code Validation
Resource        common.resource
Suite Setup     Setup lab
#Suite Teardown  Teardown virtual server

*** Variables ***
${software_version}     13.1.3

*** Keywords ***
Setup lab
    [Documentation]     Configure the lab topology for all of the test cases.
    ...                 This requires the F5s to be previously licensed.
    Log     ${software_version}
    #Setup F5 physicals
    #Setup Polatis

Setup F5 physicals
    [Documentation]     Configure the F5 physical devices, links, ip addresses.
    ...                 May or may not use a single UCS file?
    [tags]  Setup
    # Setup Primary F5
    #Connect To F5   ${f5_a}     ${USER}
    # Initial configuration
    # How can we build a yaml configuration hierarchy for the F5s basic configuration?
    # Use a .ucs file for the basic configuration?
    # Copy .ucs file to the primary f5
    # Copy .ucs file to secondary f5
    # Load ucs files to the f5s
    Log     Placeholder for F5 UCS configuration.

Setup Polatis
    [Documentation]     Configure the Polatis optical switch to configure 
    ...                 cross-connects properly for our lab ports.
    [tags]  Setup
    # Connect IXIA 11/1 to the nxs05sqsccc 4/2 port
    Cross-connect polatis port 1 to 323
    Cross-connect polatis port 193 to 131
    # Connect IXIA 11/2 to the nxs05sqsccc 4/1 port
    Cross-connect polatis port 4 to 324
    Cross-connect polatis port 196 to 132