"""Java log parser for stack traces and exceptions."""

import re
from typing import Optional

from src.parsers.base import BaseLogParser, ParsedError, StackFrame, ErrorSeverity


class JavaLogParser(BaseLogParser):
    """Parser for Java stack traces and log output."""

    # Pattern for Java exception header
    # Examples:
    #   java.lang.NullPointerException: message
    #   java.lang.NullPointerException
    #   Exception in thread "main" java.lang.RuntimeException: message
    EXCEPTION_HEADER_PATTERN = re.compile(
        r'^(?:Exception in thread "([^"]+)"\s+)?'
        r'([\w.$]+(?:Exception|Error|Throwable))'
        r'(?::\s*(.*))?$'
    )

    # Pattern for stack trace frame
    # Examples:
    #   at com.example.MyClass.myMethod(MyClass.java:42)
    #   at com.example.MyClass.myMethod(Unknown Source)
    #   at com.example.MyClass.myMethod(Native Method)
    STACK_FRAME_PATTERN = re.compile(
        r'^\s+at\s+'
        r'([\w.$<>]+)\.'  # class name
        r'([\w$<>]+)'      # method name
        r'\('
        r'([^:)]+)'        # file name or "Unknown Source" / "Native Method"
        r'(?::(\d+))?'     # optional line number
        r'\)$'
    )

    # Pattern for "Caused by" lines
    CAUSED_BY_PATTERN = re.compile(
        r'^Caused by:\s+'
        r'([\w.$]+(?:Exception|Error|Throwable))'
        r'(?::\s*(.*))?$'
    )

    # Pattern for log4j/logback style log lines
    LOG_LINE_PATTERN = re.compile(
        r'^(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:[.,]\d{3})?)\s*'  # timestamp
        r'(?:\[([^\]]+)\])?\s*'  # optional thread name
        r'(ERROR|WARN|INFO|DEBUG|TRACE)\s+'  # log level
        r'(?:([\w.]+)\s*[-:]?\s*)?'  # optional logger name
        r'(.*)$'  # message
    )

    @property
    def language(self) -> str:
        return "java"

    def can_parse(self, log_text: str) -> bool:
        """Check if the log text contains Java stack traces."""
        # Check for common Java patterns
        patterns = [
            r'at\s+[\w.$]+\.\w+\([^)]+\.java:\d+\)',  # stack frame
            r'[\w.$]+(?:Exception|Error):',  # exception with message
            r'^[\w.$]+(?:Exception|Error)$',  # exception without message
            r'Caused by:',  # caused by clause
        ]

        for pattern in patterns:
            if re.search(pattern, log_text, re.MULTILINE):
                return True
        return False

    def parse(self, log_text: str) -> list[ParsedError]:
        """Parse Java log text and extract errors."""
        errors: list[ParsedError] = []
        lines = log_text.strip().split('\n')

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines
            if not line:
                i += 1
                continue

            # Try to match log line format first (log4j/logback style)
            log_match = self.LOG_LINE_PATTERN.match(line)
            if log_match:
                timestamp, thread, level, logger, message = log_match.groups()

                # Check if this log line contains an exception
                exc_match = self.EXCEPTION_HEADER_PATTERN.match(message)
                if exc_match:
                    error, next_idx = self._parse_exception_block(
                        lines, i,
                        timestamp=timestamp,
                        thread_name=thread,
                        logger_name=logger
                    )
                    if error:
                        errors.append(error)
                    i = next_idx
                    continue

                # Check if next line starts a stack trace
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if self.EXCEPTION_HEADER_PATTERN.match(next_line):
                        error, next_idx = self._parse_exception_block(
                            lines, i + 1,
                            timestamp=timestamp,
                            thread_name=thread,
                            logger_name=logger
                        )
                        if error:
                            errors.append(error)
                        i = next_idx
                        continue

                i += 1
                continue

            # Try to match exception header directly
            exc_match = self.EXCEPTION_HEADER_PATTERN.match(line)
            if exc_match:
                error, next_idx = self._parse_exception_block(lines, i)
                if error:
                    errors.append(error)
                i = next_idx
                continue

            i += 1

        return errors

    def _parse_exception_block(
        self,
        lines: list[str],
        start_idx: int,
        timestamp: Optional[str] = None,
        thread_name: Optional[str] = None,
        logger_name: Optional[str] = None,
    ) -> tuple[Optional[ParsedError], int]:
        """Parse an exception block starting at start_idx."""
        line = lines[start_idx].strip()

        # Match the exception header
        exc_match = self.EXCEPTION_HEADER_PATTERN.match(line)
        if not exc_match:
            return None, start_idx + 1

        thread_from_header, error_type, message = exc_match.groups()
        thread_name = thread_name or thread_from_header
        message = message or ""

        # Collect raw text and stack frames
        raw_lines = [lines[start_idx]]
        stack_frames: list[StackFrame] = []

        i = start_idx + 1
        while i < len(lines):
            current_line = lines[i]
            stripped = current_line.strip()

            # Check for stack frame
            frame_match = self.STACK_FRAME_PATTERN.match(stripped)
            if frame_match:
                class_name, method_name, file_name, line_num = frame_match.groups()

                # Skip "Unknown Source" and "Native Method"
                if file_name not in ("Unknown Source", "Native Method"):
                    stack_frames.append(StackFrame(
                        file_path=file_name,
                        line_number=int(line_num) if line_num else None,
                        method_name=method_name,
                        class_name=class_name,
                    ))

                raw_lines.append(current_line)
                i += 1
                continue

            # Check for "Caused by" - stop here, it's a separate error
            if self.CAUSED_BY_PATTERN.match(stripped):
                break

            # Check for "... N more" lines
            if re.match(r'^\s*\.\.\.\s*\d+\s+more\s*$', current_line):
                raw_lines.append(current_line)
                i += 1
                continue

            # If we encounter something else, stop parsing this block
            if stripped and not stripped.startswith('\t') and not stripped.startswith('at '):
                break

            i += 1

        error = ParsedError(
            error_type=error_type,
            message=message,
            stack_frames=stack_frames,
            severity=self._determine_severity(error_type),
            raw_text='\n'.join(raw_lines),
            language=self.language,
            timestamp=timestamp,
            thread_name=thread_name,
            logger_name=logger_name,
        )

        return error, i

    def _determine_severity(self, error_type: str) -> ErrorSeverity:
        """Determine error severity based on exception type."""
        critical_types = [
            'OutOfMemoryError', 'StackOverflowError', 'VirtualMachineError',
            'LinkageError', 'ThreadDeath', 'AssertionError'
        ]

        for critical in critical_types:
            if critical in error_type:
                return ErrorSeverity.CRITICAL

        if 'Error' in error_type:
            return ErrorSeverity.CRITICAL

        return ErrorSeverity.ERROR
