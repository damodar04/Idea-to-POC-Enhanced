"""Error Handler with Retry Logic for I2POC Application"""

import logging
import time
import random
from typing import Any, Callable, Optional, Dict, List
from functools import wraps

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Handles errors with retry logic and graceful degradation"""
    
    def __init__(self):
        self.error_stats = {
            'total_errors': 0,
            'retry_successes': 0,
            'retry_failures': 0,
            'fallback_used': 0
        }
    
    def retry_with_backoff(
        self, 
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retry_on_exceptions: tuple = (Exception,),
        fallback_value: Any = None,
        fallback_message: str = None
    ):
        """
        Decorator for retrying functions with exponential backoff
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter to delays
            retry_on_exceptions: Tuple of exceptions to retry on
            fallback_value: Value to return if all retries fail
            fallback_message: Message to log when using fallback
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    
                    except retry_on_exceptions as e:
                        last_exception = e
                        self.error_stats['total_errors'] += 1
                        
                        # Check if we should retry
                        if attempt < max_retries:
                            # Calculate delay with exponential backoff
                            delay = min(
                                base_delay * (exponential_base ** attempt),
                                max_delay
                            )
                            
                            # Add jitter if enabled
                            if jitter:
                                delay = random.uniform(0, delay)
                            
                            logger.warning(
                                f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: "
                                f"{str(e)}. Retrying in {delay:.2f}s..."
                            )
                            
                            time.sleep(delay)
                        else:
                            logger.error(
                                f"All {max_retries + 1} attempts failed for {func.__name__}: {str(e)}"
                            )
                            self.error_stats['retry_failures'] += 1
                
                # All retries failed, use fallback
                if fallback_value is not None:
                    logger.warning(
                        f"Using fallback value for {func.__name__}: {fallback_message or 'Operation failed after retries'}"
                    )
                    self.error_stats['fallback_used'] += 1
                    return fallback_value
                
                # Re-raise the last exception if no fallback
                raise last_exception
            
            return wrapper
        return decorator
    
    def handle_partial_failure(self, results: Dict, failed_component: str, error_message: str) -> Dict:
        """
        Handle partial failures by continuing with available data
        
        Args:
            results: Current results dictionary
            failed_component: Name of the component that failed
            error_message: Error message to include
            
        Returns:
            Updated results with error information
        """
        if 'errors' not in results:
            results['errors'] = []
        
        results['errors'].append(f"{failed_component}: {error_message}")
        results['partial_results'] = True
        
        logger.warning(f"Partial failure in {failed_component}: {error_message}")
        
        return results
    
    def get_user_friendly_error(self, error: Exception) -> str:
        """
        Convert technical errors to user-friendly messages
        
        Args:
            error: The exception that occurred
            
        Returns:
            User-friendly error message
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        # Map common error types to user-friendly messages
        error_mapping = {
            'ConnectionError': "Unable to connect to research services. Please check your internet connection and try again.",
            'TimeoutError': "The request timed out. The research services might be temporarily unavailable.",
            'RateLimitError': "Too many requests. Please wait a moment and try again.",
            'APIError': "Research services are temporarily unavailable. Please try again later.",
            'ValueError': "Invalid input provided. Please check your request and try again.",
            'KeyError': "Required data is missing. Please try again with different parameters.",
        }
        
        # Check for specific error patterns
        if "rate limit" in error_message.lower():
            return error_mapping.get('RateLimitError', "Too many requests. Please wait and try again.")
        elif "timeout" in error_message.lower():
            return error_mapping.get('TimeoutError', "Request timed out. Please try again.")
        elif "connection" in error_message.lower():
            return error_mapping.get('ConnectionError', "Connection failed. Please check your network.")
        
        # Return mapped error or generic message
        return error_mapping.get(error_type, f"An unexpected error occurred: {error_message}")
    
    def log_error_with_context(
        self, 
        error: Exception, 
        context: Dict = None,
        level: str = 'ERROR'
    ):
        """
        Log errors with additional context for debugging
        
        Args:
            error: The exception that occurred
            context: Additional context information
            level: Logging level (ERROR, WARNING, INFO)
        """
        log_method = getattr(logger, level.lower(), logger.error)
        
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': time.time(),
        }
        
        if context:
            error_info.update(context)
        
        log_method(f"Error occurred: {error_info}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error handling statistics"""
        return self.error_stats.copy()
    
    def reset_stats(self):
        """Reset error statistics"""
        self.error_stats = {
            'total_errors': 0,
            'retry_successes': 0,
            'retry_failures': 0,
            'fallback_used': 0
        }


# Global error handler instance
error_handler = ErrorHandler()


def safe_execute(
    func: Callable,
    *args,
    fallback_value: Any = None,
    fallback_message: str = None,
    log_error: bool = True,
    **kwargs
) -> Any:
    """
    Safely execute a function with error handling
    
    Args:
        func: Function to execute
        fallback_value: Value to return on error
        fallback_message: Message to log when using fallback
        log_error: Whether to log errors
        *args, **kwargs: Function arguments
        
    Returns:
        Function result or fallback value
    """
    try:
        return func(*args, **kwargs)
    
    except Exception as e:
        if log_error:
            error_handler.log_error_with_context(e, {
                'function': func.__name__,
                'args': str(args),
                'kwargs': str(kwargs)
            })
        
        if fallback_value is not None:
            logger.warning(
                f"Using fallback for {func.__name__}: {fallback_message or str(e)}"
            )
            return fallback_value
        
        # Re-raise if no fallback
        raise


def continue_on_error(results: Dict, component: str):
    """
    Decorator to continue workflow even if a component fails
    
    Args:
        results: Results dictionary to update on error
        component: Name of the component
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            
            except Exception as e:
                error_message = error_handler.get_user_friendly_error(e)
                return error_handler.handle_partial_failure(
                    results, component, error_message
                )
        
        return wrapper
    return decorator
