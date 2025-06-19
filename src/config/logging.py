"""Simple Loguru setup with Streamlit integration - MVP approach."""

import functools
import logging
import sys
import time
from collections.abc import Callable
from pathlib import Path
from types import TracebackType
from typing import Any

import streamlit as st
from loguru import logger


def setup_logging(log_level: str = "INFO") -> None:
    """Setup minimal but effective logging with Streamlit cache protection.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Check if already setup to avoid re-configuration
    if "logging_configured" in st.session_state and st.session_state.logging_configured:
        return

    # Remove default handler
    logger.remove()

    # Console output - clean format
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
        level=log_level,
        colorize=True,
    )

    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Simple file logging with rotation
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    )

    # Intercept standard library logging (untuk Streamlit) - Simplified
    class InterceptHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            """Emit a log record by redirecting to loguru.

            Args:
                record: The log record to emit
            """
            # Simplified approach - avoid internal access
            try:
                level = record.levelname
            except Exception:
                level = "INFO"

            # Use public API only
            logger.log(level, record.getMessage())

    # Replace standard logging with Loguru - safer approach
    logging.getLogger().handlers = [InterceptHandler()]
    logging.getLogger().setLevel(logging.DEBUG)

    # Mark as configured
    st.session_state.logging_configured = True
    logger.info(
        f"Logging configured with level {log_level}. Use logger_wraps, timer, lazy_log, or LogContext for enhanced logging."
    )


def logger_wraps(*, entry: bool = True, exit: bool = True, level: str = "DEBUG"):
    """Decorator to log entry and exit of functions.

    Usage:
        @logger_wraps()
        def my_function(a, b):
            return a + b

        @logger_wraps(entry=False, level="INFO")
        def only_exit_log():
            return "result"
    """

    def wrapper(func: Callable) -> Callable:
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs) -> Any:
            # Avoid internal opt() usage - use direct logging
            if entry:
                logger.log(
                    level, f"Entering '{name}' (args={len(args)}, kwargs={len(kwargs)})"
                )

            result = func(*args, **kwargs)

            if exit:
                logger.log(level, f"Exiting '{name}' (completed)")

            return result

        return wrapped

    return wrapper


def timer(operation: str | None = None):
    """Decorator to log execution time.

    Usage:
        @timer("CSV_IMPORT")
        def import_csv():
            pass

        @timer()  # Will use function name
        def process_data():
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            op_name = operation or func.__name__.upper()
            start = time.perf_counter()

            try:
                logger.info(f"[{op_name}] Starting...")
                result = func(*args, **kwargs)
                duration = time.perf_counter() - start
                logger.info(f"[{op_name}] Completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.perf_counter() - start
                logger.error(f"[{op_name}] Failed after {duration:.3f}s: {e}")
                raise

        return wrapper

    return decorator


def lazy_log(level: str = "INFO"):
    """Lazy logging decorator - only logs if enabled.

    Simplified version without internal API access.

    Usage:
        @lazy_log("DEBUG")
        def debug_function():
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Simplified check - just log if needed
            if level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                logger.log(
                    level,
                    f"Calling {func.__name__} with {len(args)} args, {len(kwargs)} kwargs",
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator


class LogContext:
    """Context manager for logging operations.

    Usage:
        with LogContext("PROCESSING_CSV"):
            # your code here
            pass
    """

    def __init__(self, operation: str, level: str = "INFO"):
        self.operation = operation
        self.level = level
        self.start_time: float | None = None

    def __enter__(self) -> "LogContext":
        """Enter the context manager and start timing.

        Returns:
            Self for context management
        """
        self.start_time = time.perf_counter()
        logger.log(self.level, f"[{self.operation}] Starting...")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the context manager and log completion or failure.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        if self.start_time is None:
            return

        duration = time.perf_counter() - self.start_time
        if exc_type:
            logger.error(f"[{self.operation}] Failed after {duration:.3f}s: {exc_val}")
        else:
            logger.log(self.level, f"[{self.operation}] Completed in {duration:.3f}s")


# Export the main logger and utilities
__all__ = ["setup_logging", "logger_wraps", "timer", "lazy_log", "LogContext", "logger"]
