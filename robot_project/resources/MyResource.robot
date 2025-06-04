*** Variables ***
${SOME_NUMBER}    ${123}

*** Keywords ***
Some Resource Keyword
    Log    This is a keyword from MyResource.robot
    ${local_number} =    Set Variable    ${123}
    Should Be Equal As Numbers    ${SOME_NUMBER}    ${local_number}    msg=Expected ${local_number}, got ${SOME_NUMBER}
    Should Be True  ${SOME_NUMBER} > 100    msg=Expected number to be greater than 100, got '${SOME_NUMBER}'

Resource Keyword With Some ${argument} Argument
    Log    This keyword with embedded argument '${argument}' is from MyResource.robot
    Should Be Equal As Strings    ${argument}    Embedded    
    ...    msg=Expected 'Embedded' as defined in suite level, got '${argument}'

