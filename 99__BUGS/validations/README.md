# Bug Testing Validations

## How to create new bug tests

Each bug test should be validated (reproduced) and the failed report for that bug 
should be included in a folder that matches the bug id.
This report should only contain the single test case for the validation.

Example:
robot -t id716716 f5_ltm

After the test is complete move all reports to the bug folder.

To prove that a bug is hit the report should show a "FAIL" status.
Validating the bug is fixed in new versions of code should show a "PASS" status.

## Required keywords

You must show the system version in the Setup Bug keyword.

```
*** Keywords ***
Setup Bug
    tmsh show sys version
```

You may include an additional readme.md file in the bug folder to explain the setup, etc.
