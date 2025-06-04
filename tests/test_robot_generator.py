import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, call
from click.testing import CliRunner
import subprocess

from robot_generator import (
        create_robot_project,
        BASE_ROBOT_TEMPLATE,
        TEST_CASE_1,
        TEST_CASE_2,
        TEST_CASE_3,
        MY_LIBRARY_CONTENT,
        MY_RESOURCE_CONTENT
    )


class TestRobotProjectGenerator:
    """Test suite for Robot Framework project generator."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def runner(self):
        """Create a Click test runner."""
        return CliRunner()

    def test_basic_project_creation(self, runner, temp_dir):
        """Test basic project creation without additional options."""
        result = runner.invoke(create_robot_project, [
            '--project-dir', temp_dir
        ])
        
        # Print result output for debugging if test fails
        if result.exit_code != 0:
            print(f"Command failed with exit code {result.exit_code}")
            print(f"Output: {result.output}")
            if result.exception:
                print(f"Exception: {result.exception}")
                import traceback
                traceback.print_exception(type(result.exception), result.exception, result.exception.__traceback__)
        
        assert result.exit_code == 0
        assert f"Creating Robot Framework project in: {temp_dir}" in result.output
        
        # Check directory structure
        assert os.path.exists(os.path.join(temp_dir, 'tests'))
        assert os.path.exists(os.path.join(temp_dir, 'tests', 'MySuite.robot'))
        
        # Check file content
        with open(os.path.join(temp_dir, 'tests', 'MySuite.robot'), 'r') as f:
            content = f.read()
            assert "*** Settings ***" in content
            assert "*** Test Cases ***" in content
            assert "Sample Test Case With Local Keyword" in content
            assert "Some Local Keyword" in content

    def test_custom_suite_name(self, runner, temp_dir):
        """Test project creation with custom suite name."""
        custom_name = "CustomTest.robot"
        result = runner.invoke(create_robot_project, [
            '--project-dir', temp_dir,
            '--suite-name', custom_name
        ])
        
        assert result.exit_code == 0
        assert os.path.exists(os.path.join(temp_dir, 'tests', custom_name))

    def test_with_library_option(self, runner, temp_dir):
        """Test project creation with Python library."""
        result = runner.invoke(create_robot_project, [
            '--project-dir', temp_dir,
            '--with-lib'
        ])
        
        assert result.exit_code == 0
        
        # Check library directory and file
        lib_path = os.path.join(temp_dir, 'libraries', 'MyLibrary.py')
        assert os.path.exists(lib_path)
        
        # Check library content
        with open(lib_path, 'r') as f:
            content = f.read()
            assert "class MyLibrary:" in content
            assert "@keyword('Some Library Keyword')" in content
        
        # Check robot file includes library
        with open(os.path.join(temp_dir, 'tests', 'MySuite.robot'), 'r') as f:
            content = f.read()
            assert "Library    ../libraries/MyLibrary.py" in content
            assert "Sample Test Case With Python Library Keyword" in content

    def test_with_resource_option(self, runner, temp_dir):
        """Test project creation with resource file."""
        result = runner.invoke(create_robot_project, [
            '--project-dir', temp_dir,
            '--with-resource'
        ])
        
        assert result.exit_code == 0
        
        # Check resource directory and file
        resource_path = os.path.join(temp_dir, 'resources', 'MyResource.robot')
        assert os.path.exists(resource_path)
        
        # Check resource content
        with open(resource_path, 'r') as f:
            content = f.read()
            assert "*** Variables ***" in content
            assert "Some Resource Keyword" in content
        
        # Check robot file includes resource
        with open(os.path.join(temp_dir, 'tests', 'MySuite.robot'), 'r') as f:
            content = f.read()
            assert "Resource   ../resources/MyResource.robot" in content
            assert "Sample Test Case With Resource Keyword" in content

    def test_with_both_lib_and_resource(self, runner, temp_dir):
        """Test project creation with both library and resource."""
        result = runner.invoke(create_robot_project, [
            '--project-dir', temp_dir,
            '--with-lib',
            '--with-resource'
        ])
        
        assert result.exit_code == 0
        
        # Check both files exist
        assert os.path.exists(os.path.join(temp_dir, 'libraries', 'MyLibrary.py'))
        assert os.path.exists(os.path.join(temp_dir, 'resources', 'MyResource.robot'))
        
        # Check robot file includes both
        with open(os.path.join(temp_dir, 'tests', 'MySuite.robot'), 'r') as f:
            content = f.read()
            assert "Library    ../libraries/MyLibrary.py" in content
            assert "Resource   ../resources/MyResource.robot" in content
            assert "Sample Test Case With Python Library Keyword" in content
            assert "Sample Test Case With Resource Keyword" in content

    def test_dry_run_option(self, runner, temp_dir):
        """Test dry run option - should not create files."""
        result = runner.invoke(create_robot_project, [
            '--project-dir', temp_dir,
            '--dry-run',
            '--with-lib',
            '--with-resource'
        ])
        
        assert result.exit_code == 0
        assert f"Creating Robot Framework project in: {temp_dir}" in result.output
        
        # No files should be created
        assert not os.path.exists(os.path.join(temp_dir, 'tests'))
        assert not os.path.exists(os.path.join(temp_dir, 'libraries'))
        assert not os.path.exists(os.path.join(temp_dir, 'resources'))

    @patch('subprocess.run')
    def test_run_option(self, mock_subprocess, runner, temp_dir):
        """Test running the test suite."""
        mock_subprocess.return_value = None
        
        result = runner.invoke(create_robot_project, [
            '--project-dir', temp_dir,
            '--run'
        ])
        
        assert result.exit_code == 0
        assert "Running test suite..." in result.output
        
        # Check subprocess was called with correct arguments
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert call_args[0] == 'robot'
        assert '--outputdir' in call_args
        assert f'{temp_dir}/results' in call_args
        assert f'{temp_dir}/tests' in call_args

    @patch('subprocess.run')
    def test_run_option_with_subprocess_error(self, mock_subprocess, runner, temp_dir):
        """Test handling of subprocess errors when running tests."""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, 'robot')
        
        result = runner.invoke(create_robot_project, [
            '--project-dir', temp_dir,
            '--run'
        ])
        
        # Should exit with error code due to subprocess failure
        assert result.exit_code != 0

    def test_open_log_option_without_run(self, runner, temp_dir):
        """Test open-log option without run option."""
        result = runner.invoke(create_robot_project, [
            '--project-dir', temp_dir,
            '--open-log'
        ])
        
        assert result.exit_code == 0
        assert "Run the test suite first to generate log files." in result.output

    @patch('webbrowser.open')
    @patch('subprocess.run')
    def test_open_log_file_not_found(self, mock_subprocess, mock_webbrowser, runner, temp_dir):
        """Test handling when log file doesn't exist."""
        mock_subprocess.return_value = None
        
        result = runner.invoke(create_robot_project, [
            '--project-dir', temp_dir,
            '--run',
            '--open-log'
        ])
        
        assert result.exit_code == 0
        assert "not found!" in result.output
        mock_webbrowser.open.assert_not_called()

    def test_template_content_structure(self):
        """Test that template content has expected structure."""
        assert "*** Settings ***" in BASE_ROBOT_TEMPLATE
        assert "*** Variables ***" in BASE_ROBOT_TEMPLATE
        assert "*** Test Cases ***" in BASE_ROBOT_TEMPLATE
        assert "*** Keywords ***" in BASE_ROBOT_TEMPLATE
        assert "{settings_block}" in BASE_ROBOT_TEMPLATE
        assert "{test_cases}" in BASE_ROBOT_TEMPLATE

    def test_library_content_structure(self):
        """Test library content has proper Python structure."""
        assert "class MyLibrary:" in MY_LIBRARY_CONTENT
        assert "@library(" in MY_LIBRARY_CONTENT
        assert "@keyword(" in MY_LIBRARY_CONTENT
        assert "def library_keyword(self):" in MY_LIBRARY_CONTENT

    def test_resource_content_structure(self):
        """Test resource content has proper Robot Framework structure."""
        assert "*** Variables ***" in MY_RESOURCE_CONTENT
        assert "*** Keywords ***" in MY_RESOURCE_CONTENT
        assert "${SOME_NUMBER}" in MY_RESOURCE_CONTENT

    def test_all_test_cases_content(self):
        """Test individual test case templates."""
        assert "Sample Test Case With Local Keyword" in TEST_CASE_1
        assert "Sample Test Case With Python Library Keyword" in TEST_CASE_2
        assert "Sample Test Case With Resource Keyword" in TEST_CASE_3

    @patch('os.makedirs')
    def test_directory_creation_error_handling(self, mock_makedirs, runner):
        """Test handling of directory creation errors."""
        mock_makedirs.side_effect = OSError("Permission denied")
        
        result = runner.invoke(create_robot_project, [
            '--project-dir', '/invalid/path'
        ])
        
        # Should exit with error due to directory creation failure
        assert result.exit_code != 0

    def test_existing_directory_handling(self, runner, temp_dir):
        """Test that existing directories are handled properly."""
        # Create the directory first
        os.makedirs(os.path.join(temp_dir, 'tests'), exist_ok=True)
        
        result = runner.invoke(create_robot_project, [
            '--project-dir', temp_dir
        ])
        
        assert result.exit_code == 0
        assert os.path.exists(os.path.join(temp_dir, 'tests', 'MySuite.robot'))

    def test_file_encoding(self, runner, temp_dir):
        """Test that files are created with proper UTF-8 encoding."""
        result = runner.invoke(create_robot_project, [
            '--project-dir', temp_dir,
            '--with-lib',
            '--with-resource'
        ])
        
        assert result.exit_code == 0
        
        # Test that files can be read with UTF-8 encoding
        files_to_check = [
            os.path.join(temp_dir, 'tests', 'MySuite.robot'),
            os.path.join(temp_dir, 'libraries', 'MyLibrary.py'),
            os.path.join(temp_dir, 'resources', 'MyResource.robot')
        ]
        
        for file_path in files_to_check:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert len(content) > 0

    def test_command_help(self, runner):
        """Test that help command works."""
        result = runner.invoke(create_robot_project, ['--help'])
        
        assert result.exit_code == 0
        assert "Generates a Robot Framework test suite" in result.output
        assert "--project-dir" in result.output
        assert "--suite-name" in result.output
        assert "--run" in result.output
        assert "--with-lib" in result.output
        assert "--with-resource" in result.output
        assert "--open-log" in result.output
        assert "--dry-run" in result.output


class TestTemplateFormatting:
    """Test template formatting and content generation."""

    def test_settings_block_formatting_no_options(self):
        """Test settings block when no options are provided."""
        settings = []
        settings_block = "\n".join(settings)
        
        formatted = BASE_ROBOT_TEMPLATE.format(
            settings_block=settings_block,
            test_cases=TEST_CASE_1
        )
        
        # Should have empty settings section
        assert "*** Settings ***\nDocumentation" in formatted

    def test_settings_block_formatting_with_lib(self):
        """Test settings block with library option."""
        settings = ["Library    ../libraries/MyLibrary.py"]
        settings_block = "\n".join(settings)
        
        formatted = BASE_ROBOT_TEMPLATE.format(
            settings_block=settings_block,
            test_cases=TEST_CASE_1
        )
        
        assert "Library    ../libraries/MyLibrary.py" in formatted

    def test_settings_block_formatting_with_resource(self):
        """Test settings block with resource option."""
        settings = ["Resource   ../resources/MyResource.robot"]
        settings_block = "\n".join(settings)
        
        formatted = BASE_ROBOT_TEMPLATE.format(
            settings_block=settings_block,
            test_cases=TEST_CASE_1
        )
        
        assert "Resource   ../resources/MyResource.robot" in formatted

    def test_test_cases_combination(self):
        """Test different combinations of test cases."""
        # Only basic test case
        combined = TEST_CASE_1
        assert "Sample Test Case With Local Keyword" in combined
        
        # With library test case
        combined = TEST_CASE_1 + TEST_CASE_2
        assert "Sample Test Case With Local Keyword" in combined
        assert "Sample Test Case With Python Library Keyword" in combined
        
        # With all test cases
        combined = TEST_CASE_1 + TEST_CASE_2 + TEST_CASE_3
        assert "Sample Test Case With Local Keyword" in combined
        assert "Sample Test Case With Python Library Keyword" in combined
        assert "Sample Test Case With Resource Keyword" in combined
