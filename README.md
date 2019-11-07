# Functional testing of F5 load-balancers using the Robot Framework

## Why?

To expedite testing feature functionality of the F5 Networks platforms so we can
increase operational agility and return test results to operations faster for upcoming
code versions.

## F5Rest.py module

A module that uses the F5 REST API to configure and gather information from an F5 appliance.

## IxLoadRobot.py module

A module that uses the IXLoad REST API to load tests local to the server and run them.

## Polatis.py module

A module that allows modifying Polatis cross-connects using robot keywords.

# BUGS Folder

Specific bug tests for the F5 platform are placed in the /bugs folder.
To disable a specific test (in any folder) add an _ in front of the file name.

# Generic Robot Guides

"How to Write Good Test Cases":

https://github.com/robotframework/HowToWriteGoodTestCases/blob/master/HowToWriteGoodTestCases.rst

You can see some of my proposed @keyword('') decorators in Arista.py.
They may be a better method to the more difficult to read CLI inputs, etc.