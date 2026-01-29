"""Tests for log parsers."""

import pytest

from src.parsers.base import ParsedError, StackFrame, ErrorSeverity
from src.parsers.java import JavaLogParser
from src.parsers.python import PythonLogParser
from src.parsers.detector import detect_language, LanguageType, auto_parse


class TestJavaLogParser:
    """Tests for Java log parser."""

    @pytest.fixture
    def parser(self) -> JavaLogParser:
        return JavaLogParser()

    def test_parse_simple_npe(self, parser: JavaLogParser) -> None:
        """Test parsing simple NullPointerException."""
        log = """java.lang.NullPointerException: Cannot invoke method on null
\tat com.example.UserService.getUser(UserService.java:42)
\tat com.example.UserController.show(UserController.java:28)"""

        errors = parser.parse(log)

        assert len(errors) == 1
        error = errors[0]
        assert error.error_type == "java.lang.NullPointerException"
        assert error.message == "Cannot invoke method on null"
        assert error.language == "java"
        assert len(error.stack_frames) == 2
        assert error.file_path == "UserService.java"
        assert error.line_number == 42

    def test_parse_npe_without_message(self, parser: JavaLogParser) -> None:
        """Test parsing NullPointerException without message."""
        log = """java.lang.NullPointerException
\tat com.example.Service.process(Service.java:100)"""

        errors = parser.parse(log)

        assert len(errors) == 1
        assert errors[0].error_type == "java.lang.NullPointerException"
        assert errors[0].message == ""

    def test_parse_with_thread_info(self, parser: JavaLogParser) -> None:
        """Test parsing exception with thread info."""
        log = """Exception in thread "main" java.lang.RuntimeException: Test error
\tat com.example.Main.main(Main.java:10)"""

        errors = parser.parse(log)

        assert len(errors) == 1
        assert errors[0].thread_name == "main"
        assert errors[0].error_type == "java.lang.RuntimeException"

    def test_parse_sql_exception(self, parser: JavaLogParser) -> None:
        """Test parsing SQLException."""
        log = """java.sql.SQLException: Connection refused to host: localhost:3306
\tat com.mysql.jdbc.ConnectionImpl.createNewIO(ConnectionImpl.java:800)
\tat com.example.DatabaseService.connect(DatabaseService.java:45)"""

        errors = parser.parse(log)

        assert len(errors) == 1
        assert "SQLException" in errors[0].error_type
        assert "Connection refused" in errors[0].message

    def test_parse_outofmemory_error(self, parser: JavaLogParser) -> None:
        """Test parsing OutOfMemoryError with critical severity."""
        log = """java.lang.OutOfMemoryError: Java heap space
\tat com.example.DataProcessor.process(DataProcessor.java:150)"""

        errors = parser.parse(log)

        assert len(errors) == 1
        assert errors[0].error_type == "java.lang.OutOfMemoryError"
        assert errors[0].severity == ErrorSeverity.CRITICAL

    def test_parse_log4j_format(self, parser: JavaLogParser) -> None:
        """Test parsing log4j format logs."""
        log = """2024-01-15 10:30:45,123 [main] ERROR com.example.App - Error occurred
java.lang.IllegalArgumentException: Invalid input
\tat com.example.Validator.validate(Validator.java:30)"""

        errors = parser.parse(log)

        assert len(errors) == 1
        assert errors[0].error_type == "java.lang.IllegalArgumentException"
        assert errors[0].timestamp == "2024-01-15 10:30:45,123"

    def test_can_parse_java_log(self, parser: JavaLogParser) -> None:
        """Test can_parse method for Java logs."""
        java_log = """java.lang.NullPointerException
\tat com.example.Test.test(Test.java:10)"""

        python_log = """Traceback (most recent call last):
  File "test.py", line 10, in test
    raise ValueError("test")
ValueError: test"""

        assert parser.can_parse(java_log) is True
        assert parser.can_parse(python_log) is False


class TestPythonLogParser:
    """Tests for Python log parser."""

    @pytest.fixture
    def parser(self) -> PythonLogParser:
        return PythonLogParser()

    def test_parse_simple_keyerror(self, parser: PythonLogParser) -> None:
        """Test parsing simple KeyError."""
        log = """Traceback (most recent call last):
  File "app/services/user.py", line 28, in get_user
    return data['user_id']
KeyError: 'user_id'"""

        errors = parser.parse(log)

        assert len(errors) == 1
        error = errors[0]
        assert error.error_type == "KeyError"
        assert error.message == "'user_id'"
        assert error.language == "python"
        assert error.file_path == "app/services/user.py"
        assert error.line_number == 28

    def test_parse_import_error(self, parser: PythonLogParser) -> None:
        """Test parsing ImportError."""
        log = """Traceback (most recent call last):
  File "main.py", line 1, in <module>
    import pandas
ModuleNotFoundError: No module named 'pandas'"""

        errors = parser.parse(log)

        assert len(errors) == 1
        assert errors[0].error_type == "ModuleNotFoundError"
        assert "pandas" in errors[0].message

    def test_parse_type_error(self, parser: PythonLogParser) -> None:
        """Test parsing TypeError."""
        log = """Traceback (most recent call last):
  File "calc.py", line 5, in add
    return x + y
TypeError: unsupported operand type(s) for +: 'int' and 'str'"""

        errors = parser.parse(log)

        assert len(errors) == 1
        assert errors[0].error_type == "TypeError"
        assert "unsupported operand" in errors[0].message

    def test_parse_recursion_error(self, parser: PythonLogParser) -> None:
        """Test parsing RecursionError."""
        log = """Traceback (most recent call last):
  File "recursive.py", line 3, in factorial
    return n * factorial(n - 1)
  File "recursive.py", line 3, in factorial
    return n * factorial(n - 1)
RecursionError: maximum recursion depth exceeded"""

        errors = parser.parse(log)

        assert len(errors) == 1
        assert errors[0].error_type == "RecursionError"

    def test_parse_connection_error(self, parser: PythonLogParser) -> None:
        """Test parsing ConnectionError."""
        log = """Traceback (most recent call last):
  File "api_client.py", line 15, in fetch
    response = requests.get(url)
ConnectionError: HTTPSConnectionPool host='api.example.com': connection refused"""

        errors = parser.parse(log)

        assert len(errors) == 1
        assert errors[0].error_type == "ConnectionError"

    def test_parse_with_code_context(self, parser: PythonLogParser) -> None:
        """Test parsing traceback with code context."""
        log = """Traceback (most recent call last):
  File "test.py", line 10, in test_func
    result = calculate(x, y)
  File "calc.py", line 5, in calculate
    return x / y
ZeroDivisionError: division by zero"""

        errors = parser.parse(log)

        assert len(errors) == 1
        # First frame should have code context
        assert errors[0].stack_frames[0].code_context is not None

    def test_can_parse_python_log(self, parser: PythonLogParser) -> None:
        """Test can_parse method for Python logs."""
        python_log = """Traceback (most recent call last):
  File "test.py", line 10, in test
    raise ValueError("test")
ValueError: test"""

        java_log = """java.lang.NullPointerException
\tat com.example.Test.test(Test.java:10)"""

        assert parser.can_parse(python_log) is True
        assert parser.can_parse(java_log) is False


class TestLanguageDetector:
    """Tests for language detection."""

    def test_detect_java(self) -> None:
        """Test detecting Java logs."""
        log = """java.lang.NullPointerException: test
\tat com.example.Test.test(Test.java:10)"""

        assert detect_language(log) == LanguageType.JAVA

    def test_detect_python(self) -> None:
        """Test detecting Python logs."""
        log = """Traceback (most recent call last):
  File "test.py", line 10, in test
ValueError: test"""

        assert detect_language(log) == LanguageType.PYTHON

    def test_detect_unknown(self) -> None:
        """Test detecting unknown language."""
        log = """Some random text without any stack trace patterns"""

        assert detect_language(log) == LanguageType.UNKNOWN

    def test_detect_empty(self) -> None:
        """Test detecting empty input."""
        assert detect_language("") == LanguageType.UNKNOWN
        assert detect_language("   ") == LanguageType.UNKNOWN

    def test_auto_parse_java(self) -> None:
        """Test auto_parse with Java log."""
        log = """java.lang.NullPointerException: test
\tat com.example.Test.test(Test.java:10)"""

        language, errors = auto_parse(log)

        assert language == LanguageType.JAVA
        assert len(errors) == 1
        assert errors[0].error_type == "java.lang.NullPointerException"

    def test_auto_parse_python(self) -> None:
        """Test auto_parse with Python log."""
        log = """Traceback (most recent call last):
  File "test.py", line 10, in test
    raise ValueError("test")
ValueError: test"""

        language, errors = auto_parse(log)

        assert language == LanguageType.PYTHON
        assert len(errors) == 1
        assert errors[0].error_type == "ValueError"


class TestParsedError:
    """Tests for ParsedError data class."""

    def test_to_dict(self) -> None:
        """Test converting ParsedError to dictionary."""
        error = ParsedError(
            error_type="TestError",
            message="Test message",
            stack_frames=[
                StackFrame(
                    file_path="test.py",
                    line_number=10,
                    method_name="test_func"
                )
            ],
            language="python"
        )

        data = error.to_dict()

        assert data["error_type"] == "TestError"
        assert data["message"] == "Test message"
        assert data["file_path"] == "test.py"
        assert data["line_number"] == 10
        assert len(data["stack_frames"]) == 1

    def test_root_cause_frame(self) -> None:
        """Test getting root cause frame."""
        error = ParsedError(
            error_type="TestError",
            message="Test",
            stack_frames=[
                StackFrame(file_path="first.py", line_number=1),
                StackFrame(file_path="second.py", line_number=2),
            ],
            language="python"
        )

        assert error.root_cause_frame.file_path == "first.py"
        assert error.file_path == "first.py"
        assert error.line_number == 1

    def test_empty_stack_frames(self) -> None:
        """Test error with no stack frames."""
        error = ParsedError(
            error_type="TestError",
            message="Test",
            language="python"
        )

        assert error.root_cause_frame is None
        assert error.file_path is None
        assert error.line_number is None
