"""Base classes for log parsers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class ErrorSeverity(str, Enum):
    """Error severity levels."""

    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class StackFrame:
    """Represents a single frame in a stack trace."""

    file_path: str
    line_number: Optional[int] = None
    method_name: Optional[str] = None
    class_name: Optional[str] = None
    code_context: Optional[str] = None

    def __str__(self) -> str:
        parts = []
        if self.class_name:
            parts.append(self.class_name)
        if self.method_name:
            parts.append(f".{self.method_name}()")
        if self.file_path:
            location = self.file_path
            if self.line_number:
                location += f":{self.line_number}"
            parts.append(f" at {location}")
        return "".join(parts)


@dataclass
class ParsedError:
    """Represents a parsed error from log output."""

    error_type: str
    message: str
    stack_frames: list[StackFrame] = field(default_factory=list)
    severity: ErrorSeverity = ErrorSeverity.ERROR
    raw_text: str = ""
    language: str = "unknown"
    timestamp: Optional[str] = None
    thread_name: Optional[str] = None
    logger_name: Optional[str] = None

    @property
    def root_cause_frame(self) -> Optional[StackFrame]:
        """Get the frame that likely caused the error (first frame in stack)."""
        return self.stack_frames[0] if self.stack_frames else None

    @property
    def file_path(self) -> Optional[str]:
        """Get the file path from the root cause frame."""
        frame = self.root_cause_frame
        return frame.file_path if frame else None

    @property
    def line_number(self) -> Optional[int]:
        """Get the line number from the root cause frame."""
        frame = self.root_cause_frame
        return frame.line_number if frame else None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "error_type": self.error_type,
            "message": self.message,
            "severity": self.severity.value,
            "language": self.language,
            "timestamp": self.timestamp,
            "thread_name": self.thread_name,
            "logger_name": self.logger_name,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "stack_frames": [
                {
                    "file_path": f.file_path,
                    "line_number": f.line_number,
                    "method_name": f.method_name,
                    "class_name": f.class_name,
                    "code_context": f.code_context,
                }
                for f in self.stack_frames
            ],
            "raw_text": self.raw_text,
        }


class BaseLogParser(ABC):
    """Abstract base class for log parsers."""

    @property
    @abstractmethod
    def language(self) -> str:
        """Return the language this parser handles."""
        pass

    @abstractmethod
    def parse(self, log_text: str) -> list[ParsedError]:
        """
        Parse log text and extract errors.

        Args:
            log_text: Raw log text to parse

        Returns:
            List of ParsedError objects
        """
        pass

    @abstractmethod
    def can_parse(self, log_text: str) -> bool:
        """
        Check if this parser can handle the given log text.

        Args:
            log_text: Raw log text to check

        Returns:
            True if this parser can handle the log text
        """
        pass

    def _extract_multiline_block(
        self,
        lines: list[str],
        start_idx: int,
        is_continuation: callable
    ) -> tuple[list[str], int]:
        """
        Extract a multiline block starting from start_idx.

        Args:
            lines: List of log lines
            start_idx: Starting line index
            is_continuation: Function to check if a line is a continuation

        Returns:
            Tuple of (block lines, next index to process)
        """
        block = [lines[start_idx]]
        idx = start_idx + 1

        while idx < len(lines) and is_continuation(lines[idx]):
            block.append(lines[idx])
            idx += 1

        return block, idx
