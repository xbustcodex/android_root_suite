"""
Thread utility functions
"""

import threading
from typing import Callable, Any

def run_in_thread(func: Callable, *args, **kwargs) -> threading.Thread:
    """
    Run function in a separate thread
    
    Args:
        func: Function to run
        *args: Function arguments
        **kwargs: Function keyword arguments
    
    Returns:
        Started thread
    """
    thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
    thread.start()
    return thread

def run_with_callback(func: Callable, callback: Callable, *args, **kwargs):
    """
    Run function in thread and call callback with result
    
    Args:
        func: Function to run
        callback: Callback function to call with result
        *args: Function arguments
        **kwargs: Function keyword arguments
    """
    def wrapper():
        try:
            result = func(*args, **kwargs)
            callback(result)
        except Exception as e:
            callback(None, e)
    
    return run_in_thread(wrapper)
