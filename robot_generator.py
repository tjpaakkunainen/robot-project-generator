import click
import subprocess
import webbrowser
import os

# === Base template with placeholders ===
BASE_ROBOT_TEMPLATE = """
*** Settings ***
Documentation   This is an auto-generated Robot Framework test suite.
{settings_block}

*** Variables ***
${{SOME_VARIABLE}}      Hello from some placeholder variable!

*** Test Cases ***
{test_cases}

*** Keywords ***
Some Local Keyword
    Log    ${{SOME_VARIABLE}}
    Should Not Be Empty    ${{SOME_VARIABLE}}    msg=Expected non-empty value!
    Should Be Equal As Strings    ${{SOME_VARIABLE}}    Hello from some placeholder variable!
    ...    msg=Expected string 'Hello from some placeholder variable!', got '${{SOME_VARIABLE}}'
    Should Contain    ${{SOME_VARIABLE}}    Hello    msg=Expected string to contain 'Hello', got '${{SOME_VARIABLE}}'
"""

# === Individual test cases ===
TEST_CASE_1 = """Sample Test Case With Local Keyword
    Some Local Keyword
"""

TEST_CASE_2 = """
Sample Test Case With Python Library Keyword
    Some Library Keyword
    Another Library Keyword
    Verify ${101} Is Greater Than ${100}
"""

TEST_CASE_3 = """
Sample Test Case With Resource Keyword
    Some Resource Keyword
    Resource Keyword With Some Embedded Argument
"""


# === Python library content ===
MY_LIBRARY_CONTENT = """from robot.api import logger
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
"""

# === Resource file content ===
MY_RESOURCE_CONTENT = """*** Variables ***
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

"""


@click.command()
@click.option(
    "--project-dir",
    default="robot_project",
    help="Directory to create the Robot Framework project in.",
)
@click.option(
    "--suite-name",
    default="MySuite.robot",
    help="Name of the Robot Framework file to generate.",
)
@click.option(
    "--run", is_flag=True, help="Run the generated Robot Framework test suite."
)
@click.option(
    "--open-log", is_flag=True, help="Open the log file after running the test suite."
)
@click.option(
    "--dry-run", is_flag=True, help="Perform a dry run without creating files."
)
@click.option(
    "--with-lib",
    is_flag=True,
    help="Include custom Python library (libraries/MyLibrary.py).",
)
@click.option(
    "--with-resource",
    is_flag=True,
    help="Include custom resource file (resources/MyResource.robot).",
)
def create_robot_project(
    suite_name, run, open_log, dry_run, with_lib, with_resource, project_dir
):
    """Generates a Robot Framework test suite with optional library and resource."""

    click.echo(f"Creating Robot Framework project in: {project_dir}")
    if not dry_run:
        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(f"{project_dir}/tests", exist_ok=True)
        click.echo("...Project directory created.")

    # === Settings block based on user flags ===
    settings = []
    if with_lib:
        settings.append("Library    ../libraries/MyLibrary.py")
    if with_resource:
        settings.append("Resource   ../resources/MyResource.robot")
    settings_block = "\n".join(settings)

    # === Assemble test cases and keywords ===
    test_cases = TEST_CASE_1

    if with_lib:
        test_cases += TEST_CASE_2

    if with_resource:
        test_cases += TEST_CASE_3

    # === Fill final content ===
    robot_content = BASE_ROBOT_TEMPLATE.format(
        settings_block=settings_block,
        test_cases=test_cases,
    )

    # === Write Robot Framework test suite ===
    robot_path = os.path.join(project_dir, "tests", suite_name)
    click.echo(f"Creating Robot Framework test file at: {robot_path}")
    if not dry_run:
        with open(robot_path, "w", encoding="utf-8") as f:
            f.write(robot_content)
        click.echo(f"...Robot test file created.")

    # === Optional: write additional files ===
    if with_lib:
        lib_dir = os.path.join(project_dir, "libraries")
        click.echo(f"Creating Python library file at: {lib_dir}/MyLibrary.py")
        if not dry_run:
            os.makedirs(lib_dir, exist_ok=True)
            with open(os.path.join(lib_dir, "MyLibrary.py"), "w", encoding="utf-8") as f:
                f.write(MY_LIBRARY_CONTENT)
            click.echo("...Python library file created")

    if with_resource:
        resource_dir = os.path.join(project_dir, "resources")
        click.echo(f"Creating resource file at: {resource_dir}/MyResource.robot")
        if not dry_run:
            os.makedirs(resource_dir, exist_ok=True)
            with open(os.path.join(resource_dir, "MyResource.robot"), "w", encoding="utf-8") as f:
                f.write(MY_RESOURCE_CONTENT)
            click.echo(f"...Resource file created")

    if run:
        results_dir = os.path.join(project_dir, "results")
        os.makedirs(results_dir, exist_ok=True)
        click.echo("Running test suite...")
        try:
            subprocess.run(
                [
                    "robot",
                    "--outputdir",
                    results_dir,
                    "--loglevel",
                    "TRACE:INFO",
                    "--pythonpath",
                    project_dir,
                    f"{project_dir}/tests",
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            click.echo(f"Error running Robot Framework test suite: {e}")
            raise

    if open_log:
        if not run:
            click.echo("Run the test suite first to generate log files.")
            return
        log_path = os.path.abspath(f"{results_dir}/log.html")
        if os.path.exists(log_path):
            click.echo(f"Opening log file: {log_path}")
            webbrowser.open(f"file://{log_path}")
        else:
            click.echo(f"{log_path} not found!")


if __name__ == "__main__":
    create_robot_project()
