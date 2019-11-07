# https://cdn.f5.com/product/bugtracker/ID716716.html
*** Settings ***
Resource    ../common.resource
Library     ../F5Rest.py  ${f5_primary}     ${user}

*** Test Cases ***
ID716716
    [Documentation]     Bug ID 716716: Under certain circumstances
    ...                 having a kernel route but no TMM route can lead to a TMM core
    # tmsh commands to setup for bug
    # wait 120
    # Make sure there are not core dump files