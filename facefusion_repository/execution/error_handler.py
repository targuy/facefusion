"""
Error handler with retry and recovery mechanisms.
"""

import time
from typing import Callable, List, Optional, TypeVar

T = TypeVar('T')


class ErrorHandler:
    """
    Handles errors during batch processing with retry logic.

    Provides mechanisms for graceful error handling, retry with backoff,
    and error logging.
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        backoff_multiplier: float = 2.0
    ) -> None:
        """
        Initialize error handler.

        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries in seconds
            backoff_multiplier: Multiplier for exponential backoff
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff_multiplier = backoff_multiplier
        self._errors: List[str] = []

    def execute_with_retry(
        self,
        func: Callable[[], T],
        operation_name: str = 'Operation',
        on_retry: Optional[Callable[[int, Exception], None]] = None
    ) -> Optional[T]:
        """
        Execute a function with retry logic.

        Args:
            func: Function to execute
            operation_name: Name of operation for logging
            on_retry: Optional callback called on each retry

        Returns:
            Result of function, or None if all retries failed
        """
        last_exception: Optional[Exception] = None
        delay = self.retry_delay

        for attempt in range(self.max_retries + 1):
            try:
                return func()

            except Exception as e:
                last_exception = e

                if attempt < self.max_retries:
                    error_msg = f'{operation_name} failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}'
                    self.log_error(error_msg)

                    if on_retry:
                        on_retry(attempt + 1, e)

                    # Wait before retry with exponential backoff
                    time.sleep(delay)
                    delay *= self.backoff_multiplier
                else:
                    # Final attempt failed
                    error_msg = f'{operation_name} failed after {self.max_retries + 1} attempts: {e}'
                    self.log_error(error_msg)

        return None

    def log_error(self, error_message: str) -> None:
        """
        Log an error message.

        Args:
            error_message: Error message to log
        """
        self._errors.append(error_message)
        print(f'ERROR: {error_message}')

    def get_errors(self) -> List[str]:
        """
        Get all logged errors.

        Returns:
            List of error messages
        """
        return self._errors.copy()

    def get_error_count(self) -> int:
        """
        Get number of logged errors.

        Returns:
            Error count
        """
        return len(self._errors)

    def clear_errors(self) -> None:
        """Clear all logged errors."""
        self._errors.clear()

    def has_errors(self) -> bool:
        """
        Check if any errors have been logged.

        Returns:
            True if errors exist
        """
        return len(self._errors) > 0

    def get_error_summary(self) -> str:
        """
        Get formatted summary of all errors.

        Returns:
            Human-readable error summary
        """
        if not self._errors:
            return 'No errors recorded'

        summary = f'Total errors: {len(self._errors)}\n\n'
        summary += 'Error details:\n'

        for i, error in enumerate(self._errors, 1):
            summary += f'{i}. {error}\n'

        return summary

    @staticmethod
    def is_retryable_error(exception: Exception) -> bool:
        """
        Determine if an error is worth retrying.

        Args:
            exception: Exception to check

        Returns:
            True if error is retryable
        """
        # Transient errors that are worth retrying
        retryable_types = (
            IOError,
            OSError,
            ConnectionError,
            TimeoutError
        )

        # Check exception type
        if isinstance(exception, retryable_types):
            return True

        # Check error messages for transient issues
        error_msg = str(exception).lower()
        transient_patterns = [
            'timeout',
            'connection',
            'network',
            'temporary',
            'busy',
            'locked'
        ]

        return any(pattern in error_msg for pattern in transient_patterns)

    def execute_with_fallback(
        self,
        primary_func: Callable[[], T],
        fallback_func: Callable[[], T],
        operation_name: str = 'Operation'
    ) -> Optional[T]:
        """
        Execute a function with fallback on failure.

        Args:
            primary_func: Primary function to try
            fallback_func: Fallback function if primary fails
            operation_name: Name of operation for logging

        Returns:
            Result from primary or fallback function
        """
        # Try primary function with retry
        result = self.execute_with_retry(primary_func, operation_name)

        if result is not None:
            return result

        # Primary failed, try fallback
        try:
            self.log_error(f'{operation_name} primary method failed, trying fallback')
            return fallback_func()

        except Exception as e:
            error_msg = f'{operation_name} fallback also failed: {e}'
            self.log_error(error_msg)
            return None

    def wrap_with_error_handling(
        self,
        func: Callable[[], T],
        error_message: str,
        return_on_error: Optional[T] = None
    ) -> T:
        """
        Wrap a function with basic error handling.

        Args:
            func: Function to wrap
            error_message: Error message prefix
            return_on_error: Value to return on error

        Returns:
            Result of function or return_on_error value
        """
        try:
            return func()
        except Exception as e:
            self.log_error(f'{error_message}: {e}')
            return return_on_error  # type: ignore
