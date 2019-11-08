# Bug Testing Validations

## How to create new bug tests

Each bug test should be validated (reproduced) and the failed report for that bug 
should be included in a folder that matches the bug id.
This report should only contain the single test case for the validation.

Example:
robot -t id716716 f5_ltm

Move reports to folder validations/id716716

To prove that a bug is hit the report should show a "FAIL" status.
Validating the bug is fixed in a new version of code should show a "PASS" status.

## Required keywords

You must log the system version in the Setup Bug keyword.

*** Keywords ***
Setup Bug
    ${sys}              tmsh show sys version
    Log                 ${sys}

You may include an additional readme.md file in the bug folder to explain the setup, etc.
