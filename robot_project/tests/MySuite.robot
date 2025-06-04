
*** Settings ***
Documentation   This is an auto-generated Robot Framework test suite.
Library    ../libraries/MyLibrary.py
Resource   ../resources/MyResource.robot

*** Variables ***
${SOME_VARIABLE}      Hello from some placeholder variable!

*** Test Cases ***
Sample Test Case With Local Keyword
    Some Local Keyword

Sample Test Case With Python Library Keyword
    Some Library Keyword
    Another Library Keyword
    Verify ${101} Is Greater Than ${100}

Sample Test Case With Resource Keyword
    Some Resource Keyword
    Resource Keyword With Some Embedded Argument


*** Keywords ***
Some Local Keyword
    Log    ${SOME_VARIABLE}
    Should Not Be Empty    ${SOME_VARIABLE}    msg=Expected non-empty value!
    Should Be Equal As Strings    ${SOME_VARIABLE}    Hello from some placeholder variable!
    ...    msg=Expected string 'Hello from some placeholder variable!', got '${SOME_VARIABLE}'
    Should Contain    ${SOME_VARIABLE}    Hello    msg=Expected string to contain 'Hello', got '${SOME_VARIABLE}'
