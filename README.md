# Functional testing of F5 load-balancers using the Robot Framework

## Why?

To expedite testing feature functionality of the F5 Networks platforms so we can
increase operational agility and return test results to operations faster for upcoming
code versions.

## F5.py module

A module that uses bigsuds to configure and gather information from an F5 appliance.

### To Do
- Figure out best way to connect to mulitple F5s with context switching.

## Polatis.py module

A module that allows modifying Polatis cross-connects using robot keywords.

I believe test cases relying too much on CLI inputs and variable replacement are 
difficult to read, understand and modify when many of the commands in test cases
should be moved to Robot keywords.

Here is the "How to Write Good Test Cases" Robot guide:

https://github.com/robotframework/HowToWriteGoodTestCases/blob/master/HowToWriteGoodTestCases.rst

You can see some of my proposed @keyword('') decorators in Arista.py.
They may be a better method to the more difficult to read CLI inputs, etc.