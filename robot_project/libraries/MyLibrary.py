from robot.api import logger
from robot.api.deco import keyword, library

@library(scope='SUITE', version='0.1', auto_keywords=True)
class MyLibrary:

    @keyword('Some Library Keyword')
    def library_keyword(self):
        logger.info("This is a keyword from MyLibrary.py")
        assert True, "This is a simple assertion in MyLibrary.py"
    
    # auto_keywords=True allows this keyword to be automatically discovered by Robot Framework
    def another_library_keyword(self):
        logger.info("This is another keyword from MyLibrary.py")

    @keyword('Verify ${number} Is Greater Than ${threshold}')
    def do_some_number_check(self, number: int, threshold: int):

        if not isinstance(number, (int, float)):
            raise TypeError(f"Invalid type for 'number': expected int or float, got {type(number).__name__}")
        if not isinstance(threshold, (int, float)):
            raise TypeError(f"Invalid type for 'threshold': expected int or float, got {type(threshold).__name__}")

        logger.info(f"Checking if {number} is greater than {threshold}")
        if number <= threshold:
            raise AssertionError(f"Expected number greater than {threshold}, got {number}")
        return number
