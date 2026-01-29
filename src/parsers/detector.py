"""Language detection for log files."""

import re
from enum import Enum
from typing import Optional

from src.parsers.base import BaseLogParser


class LanguageType(str, Enum):
    """Supported programming languages for log parsing."""

    JAVA = "java"
    PYTHON = "python"
    UNKNOWN = "unknown"


# Java-specific patterns
JAVA_PATTERNS = [
    # Stack frame pattern: at com.example.Class.method(File.java:123)
    (r'at\s+[\w.$]+\.\w+\([^)]+\.java:\d+\)', 10),
    # Exception types: java.lang.NullPointerException
    (r'java\.\w+\.\w+(?:Exception|Error)', 8),
    # Common Java exceptions
    (r'(?:NullPointerException|ClassNotFoundException|SQLException|IOException)', 5),
    # Java package patterns
    (r'(?:com|org|net|io)\.\w+\.\w+', 3),
    # Caused by clause
    (r'Caused by:\s*[\w.$]+(?:Exception|Error)', 5),
    # Thread info: Exception in thread "main"
    (r'Exception in thread "[^"]+"', 7),
]

# Python-specific patterns
PYTHON_PATTERNS = [
    # Traceback header
    (r'Traceback \(most recent call last\):', 10),
    # File pattern: File "path.py", line 123, in function
    (r'File "[^"]+\.py", line \d+, in', 10),
    # Python exception types
    (r'(?:KeyError|ValueError|TypeError|AttributeError|ImportError|IndexError):', 7),
    # Python module patterns
    (r'(?:__\w+__|self\.\w+)', 3),
    # Python-style indentation in traceback
    (r'^\s{4,}\w+', 2),
]


def detect_language(log_text: str) -> LanguageType:
    """
    Detect the programming language from log text.

    Args:
        log_text: Raw log text to analyze

    Returns:
        LanguageType indicating the detected language
    """
    if not log_text or not log_text.strip():
        return LanguageType.UNKNOWN

    java_score = _calculate_score(log_text, JAVA_PATTERNS)
    python_score = _calculate_score(log_text, PYTHON_PATTERNS)

    # Require minimum confidence
    min_score = 5

    if java_score >= min_score and java_score > python_score:
        return LanguageType.JAVA
    elif python_score >= min_score and python_score > java_score:
        return LanguageType.PYTHON
    elif java_score >= min_score:
        return LanguageType.JAVA
    elif python_score >= min_score:
        return LanguageType.PYTHON

    return LanguageType.UNKNOWN


def _calculate_score(text: str, patterns: list[tuple[str, int]]) -> int:
    """Calculate confidence score for a language based on pattern matches."""
    score = 0
    for pattern, weight in patterns:
        matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
        if matches:
            # Add weight for each match, but cap at 3x the base weight
            score += min(len(matches) * weight, weight * 3)
    return score


def get_parser_for_language(language: LanguageType) -> Optional[BaseLogParser]:
    """
    Get the appropriate parser for a language.

    Args:
        language: The detected or specified language

    Returns:
        Parser instance or None if no parser available
    """
    from src.parsers.java import JavaLogParser
    from src.parsers.python import PythonLogParser

    parsers = {
        LanguageType.JAVA: JavaLogParser,
        LanguageType.PYTHON: PythonLogParser,
    }

    parser_class = parsers.get(language)
    return parser_class() if parser_class else None


def auto_parse(log_text: str) -> tuple[LanguageType, list]:
    """
    Automatically detect language and parse log text.

    Args:
        log_text: Raw log text to parse

    Returns:
        Tuple of (detected language, list of parsed errors)
    """
    language = detect_language(log_text)
    parser = get_parser_for_language(language)

    if parser:
        errors = parser.parse(log_text)
        return language, errors

    return language, []
