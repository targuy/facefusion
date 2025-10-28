"""
Tests for FaceFusion Repository System - Error Handler.
"""

import pytest

from facefusion_repository.execution.error_handler import ErrorHandler


def test_error_handler_initialization():
    """Test ErrorHandler initialization."""
    handler = ErrorHandler()

    assert handler.max_retries == 3
    assert handler.retry_delay == 1.0
    assert handler.backoff_multiplier == 2.0
    assert not handler.has_errors()
    assert handler.get_error_count() == 0


def test_error_handler_log_error():
    """Test logging errors."""
    handler = ErrorHandler()

    handler.log_error('Test error 1')
    handler.log_error('Test error 2')

    assert handler.has_errors()
    assert handler.get_error_count() == 2

    errors = handler.get_errors()
    assert len(errors) == 2
    assert 'Test error 1' in errors
    assert 'Test error 2' in errors


def test_error_handler_clear_errors():
    """Test clearing errors."""
    handler = ErrorHandler()

    handler.log_error('Test error')
    assert handler.has_errors()

    handler.clear_errors()
    assert not handler.has_errors()
    assert handler.get_error_count() == 0


def test_error_handler_execute_with_retry_success():
    """Test successful execution without retry."""
    handler = ErrorHandler()

    def successful_func():
        return 'success'

    result = handler.execute_with_retry(successful_func, 'Test Operation')

    assert result == 'success'
    assert not handler.has_errors()


def test_error_handler_execute_with_retry_failure():
    """Test execution that fails all retries."""
    handler = ErrorHandler(max_retries=2, retry_delay=0.01)

    def failing_func():
        raise ValueError('Test error')

    result = handler.execute_with_retry(failing_func, 'Test Operation')

    assert result is None
    assert handler.has_errors()
    assert handler.get_error_count() == 3  # Initial + 2 retries


def test_error_handler_execute_with_retry_eventual_success():
    """Test execution that succeeds after retries."""
    handler = ErrorHandler(max_retries=3, retry_delay=0.01)

    attempts = {'count': 0}

    def eventually_successful_func():
        attempts['count'] += 1
        if attempts['count'] < 3:
            raise ValueError('Not yet')
        return 'success'

    result = handler.execute_with_retry(eventually_successful_func, 'Test Operation')

    assert result == 'success'
    assert attempts['count'] == 3
    assert handler.has_errors()  # Errors were logged for failed attempts


def test_error_handler_retry_callback():
    """Test retry callback functionality."""
    handler = ErrorHandler(max_retries=2, retry_delay=0.01)

    retry_attempts = []

    def on_retry(attempt: int, exception: Exception):
        retry_attempts.append(attempt)

    def failing_func():
        raise ValueError('Test error')

    handler.execute_with_retry(
        failing_func,
        'Test Operation',
        on_retry=on_retry
    )

    assert len(retry_attempts) == 2
    assert retry_attempts == [1, 2]


def test_error_handler_is_retryable_error():
    """Test retryable error detection."""
    handler = ErrorHandler()

    # Retryable errors
    assert handler.is_retryable_error(IOError('test'))
    assert handler.is_retryable_error(OSError('test'))
    assert handler.is_retryable_error(ConnectionError('test'))
    assert handler.is_retryable_error(TimeoutError('test'))

    # Non-retryable errors
    assert not handler.is_retryable_error(ValueError('test'))
    assert not handler.is_retryable_error(TypeError('test'))

    # Retryable by message
    assert handler.is_retryable_error(Exception('timeout occurred'))
    assert handler.is_retryable_error(Exception('connection lost'))
    assert not handler.is_retryable_error(Exception('invalid value'))


def test_error_handler_execute_with_fallback_success():
    """Test fallback when primary succeeds."""
    handler = ErrorHandler(max_retries=1, retry_delay=0.01)

    def primary_func():
        return 'primary'

    def fallback_func():
        return 'fallback'

    result = handler.execute_with_fallback(
        primary_func,
        fallback_func,
        'Test Operation'
    )

    assert result == 'primary'


def test_error_handler_execute_with_fallback_use_fallback():
    """Test fallback when primary fails."""
    handler = ErrorHandler(max_retries=1, retry_delay=0.01)

    def primary_func():
        raise ValueError('Primary failed')

    def fallback_func():
        return 'fallback'

    result = handler.execute_with_fallback(
        primary_func,
        fallback_func,
        'Test Operation'
    )

    assert result == 'fallback'
    assert handler.has_errors()


def test_error_handler_execute_with_fallback_both_fail():
    """Test fallback when both primary and fallback fail."""
    handler = ErrorHandler(max_retries=1, retry_delay=0.01)

    def primary_func():
        raise ValueError('Primary failed')

    def fallback_func():
        raise ValueError('Fallback failed')

    result = handler.execute_with_fallback(
        primary_func,
        fallback_func,
        'Test Operation'
    )

    assert result is None
    assert handler.has_errors()


def test_error_handler_wrap_with_error_handling():
    """Test wrapping function with error handling."""
    handler = ErrorHandler()

    def successful_func():
        return 'success'

    def failing_func():
        raise ValueError('Test error')

    # Successful execution
    result = handler.wrap_with_error_handling(
        successful_func,
        'Test Operation',
        return_on_error='error'
    )
    assert result == 'success'

    # Failed execution
    result = handler.wrap_with_error_handling(
        failing_func,
        'Test Operation',
        return_on_error='error'
    )
    assert result == 'error'
    assert handler.has_errors()


def test_error_handler_error_summary():
    """Test error summary generation."""
    handler = ErrorHandler()

    handler.log_error('Error 1')
    handler.log_error('Error 2')
    handler.log_error('Error 3')

    summary = handler.get_error_summary()

    assert 'Total errors: 3' in summary
    assert 'Error 1' in summary
    assert 'Error 2' in summary
    assert 'Error 3' in summary


def test_error_handler_no_errors_summary():
    """Test error summary when no errors."""
    handler = ErrorHandler()

    summary = handler.get_error_summary()

    assert 'No errors recorded' in summary
