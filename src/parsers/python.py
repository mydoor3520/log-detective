"""Python log parser for stack traces and exceptions."""

import re
from typing import Optional

from src.parsers.base import BaseLogParser, ParsedError, StackFrame, ErrorSeverity


class PythonLogParser(BaseLogParser):
    """Parser for Python stack traces and log output."""

    # Pattern for Python traceback header
    TRACEBACK_HEADER_PATTERN = re.compile(
        r'^Traceback \(most recent call last\):$'
    )

    # Pattern for Python stack frame
    # Examples:
    #   File "path/to/file.py", line 42, in function_name
    #   File "/absolute/path/file.py", line 10, in <module>
    STACK_FRAME_PATTERN = re.compile(
        r'^\s*File "([^"]+)", line (\d+), in (.+)$'
    )

    # Pattern for code context line (indented code)
    CODE_CONTEXT_PATTERN = re.compile(
        r'^\s{4,}(.+)$'
    )

    # Pattern for exception line (at the end of traceback)
    # Examples:
    #   KeyError: 'user_id'
    #   ValueError: invalid literal for int()
    #   TypeError: unsupported operand type(s) for +: 'int' and 'str'
    EXCEPTION_LINE_PATTERN = re.compile(
        r'^([\w.]+(?:Error|Exception|Warning)?):?\s*(.*)$'
    )

    # Pattern for Python logging module format
    # Examples:
    #   2024-01-15 10:30:45,123 - ERROR - module_name - message
    #   2024-01-15 10:30:45 ERROR module_name message
    LOG_LINE_PATTERN = re.compile(
        r'^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(?:[.,]\d{3})?)\s*'  # timestamp
        r'[-\s]*'
        r'(ERROR|WARNING|WARN|INFO|DEBUG|CRITICAL)\s*'  # log level
        r'[-\s]*'
        r'(?:([\w.]+)\s*[-\s]*)?'  # optional logger name
        r'(.*)$'  # message
    )

    @property
    def language(self) -> str:
        return "python"

    def can_parse(self, log_text: str) -> bool:
        """Check if the log text contains Python stack traces."""
        patterns = [
            r'Traceback \(most recent call last\):',
            r'File "[^"]+", line \d+, in',
            r'^[\w.]+Error:',
            r'^[\w.]+Exception:',
        ]

        for pattern in patterns:
            if re.search(pattern, log_text, re.MULTILINE):
                return True
        return False

    def parse(self, log_text: str) -> list[ParsedError]:
        """Parse Python log text and extract errors."""
        errors: list[ParsedError] = []
        lines = log_text.strip().split('\n')

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                i += 1
                continue

            # Check for logging format
            log_match = self.LOG_LINE_PATTERN.match(stripped)
            if log_match:
                timestamp, level, logger, message = log_match.groups()

                # Check if next line is a traceback
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if self.TRACEBACK_HEADER_PATTERN.match(next_line):
                        error, next_idx = self._parse_traceback_block(
                            lines, i + 1,
                            timestamp=timestamp,
                            logger_name=logger
                        )
                        if error:
                            errors.append(error)
                        i = next_idx
                        continue

                i += 1
                continue

            # Check for traceback header
            if self.TRACEBACK_HEADER_PATTERN.match(stripped):
                error, next_idx = self._parse_traceback_block(lines, i)
                if error:
                    errors.append(error)
                i = next_idx
                continue

            # Check for standalone exception line (without traceback)
            exc_match = self.EXCEPTION_LINE_PATTERN.match(stripped)
            if exc_match and self._is_valid_exception_type(exc_match.group(1)):
                error = ParsedError(
                    error_type=exc_match.group(1),
                    message=exc_match.group(2) or "",
                    stack_frames=[],
                    severity=self._determine_severity(exc_match.group(1)),
                    raw_text=line,
                    language=self.language,
                )
                errors.append(error)
                i += 1
                continue

            i += 1

        return errors

    def _parse_traceback_block(
        self,
        lines: list[str],
        start_idx: int,
        timestamp: Optional[str] = None,
        logger_name: Optional[str] = None,
    ) -> tuple[Optional[ParsedError], int]:
        """Parse a traceback block starting at start_idx."""
        raw_lines = [lines[start_idx]]
        stack_frames: list[StackFrame] = []

        i = start_idx + 1
        current_frame: Optional[StackFrame] = None

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Check for stack frame
            frame_match = self.STACK_FRAME_PATTERN.match(stripped)
            if frame_match:
                # Save previous frame if exists
                if current_frame:
                    stack_frames.append(current_frame)

                file_path, line_num, func_name = frame_match.groups()
                current_frame = StackFrame(
                    file_path=file_path,
                    line_number=int(line_num),
                    method_name=func_name,
                )
                raw_lines.append(line)
                i += 1
                continue

            # Check for code context (follows a stack frame)
            context_match = self.CODE_CONTEXT_PATTERN.match(line)
            if context_match and current_frame:
                current_frame.code_context = context_match.group(1).strip()
                raw_lines.append(line)
                i += 1
                continue

            # Check for exception line (end of traceback)
            exc_match = self.EXCEPTION_LINE_PATTERN.match(stripped)
            if exc_match and self._is_valid_exception_type(exc_match.group(1)):
                # Save last frame
                if current_frame:
                    stack_frames.append(current_frame)

                raw_lines.append(line)

                # Reverse stack frames (Python shows most recent last)
                stack_frames.reverse()

                error = ParsedError(
                    error_type=exc_match.group(1),
                    message=exc_match.group(2) or "",
                    stack_frames=stack_frames,
                    severity=self._determine_severity(exc_match.group(1)),
                    raw_text='\n'.join(raw_lines),
                    language=self.language,
                    timestamp=timestamp,
                    logger_name=logger_name,
                )

                return error, i + 1

            # Check for "During handling of..." which indicates chained exception
            if stripped.startswith('During handling of') or stripped.startswith('The above exception'):
                # Save current frame and return what we have
                if current_frame:
                    stack_frames.append(current_frame)
                break

            # Empty line might end the traceback
            if not stripped:
                i += 1
                continue

            # Unknown line, might be end of traceback
            break

        # Handle case where we didn't find a proper exception line
        if stack_frames or current_frame:
            if current_frame and current_frame not in stack_frames:
                stack_frames.append(current_frame)
            stack_frames.reverse()

            return ParsedError(
                error_type="Unknown",
                message="Incomplete traceback",
                stack_frames=stack_frames,
                severity=ErrorSeverity.ERROR,
                raw_text='\n'.join(raw_lines),
                language=self.language,
                timestamp=timestamp,
                logger_name=logger_name,
            ), i

        return None, i

    def _is_valid_exception_type(self, type_name: str) -> bool:
        """Check if the type name looks like a valid Python exception."""
        # Must end with Error, Exception, or Warning (or be a known type)
        valid_suffixes = ('Error', 'Exception', 'Warning')
        known_types = ('KeyboardInterrupt', 'SystemExit', 'GeneratorExit', 'StopIteration')

        return (
            any(type_name.endswith(suffix) for suffix in valid_suffixes) or
            type_name in known_types
        )

    def _determine_severity(self, error_type: str) -> ErrorSeverity:
        """Determine error severity based on exception type."""
        critical_types = [
            'SystemExit', 'KeyboardInterrupt', 'MemoryError',
            'RecursionError', 'SystemError'
        ]

        warning_types = ['Warning', 'DeprecationWarning', 'FutureWarning', 'UserWarning']

        for critical in critical_types:
            if critical in error_type:
                return ErrorSeverity.CRITICAL

        for warning in warning_types:
            if warning in error_type:
                return ErrorSeverity.WARNING

        return ErrorSeverity.ERROR
