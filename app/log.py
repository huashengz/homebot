import logging
import sys
from datetime import datetime
from pathlib import Path

def setup_logging(
    level=logging.INFO,
    format_string=None,
    log_to_file=False,
    log_file_path=None,
    log_to_console=True
):
    """
    Setup logging configuration for the application
    
    Args:
        level: Logging level (default: INFO)
        format_string: Format string for log messages
        log_to_file: Whether to log to a file
        log_file_path: Path to log file (if log_to_file is True)
        log_to_console: Whether to log to console
    """
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(funcName)s() - %(message)s"
        )
    
    # Create formatter
    formatter = logging.Formatter(
        fmt=format_string,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler
    if log_to_file:
        if log_file_path is None:
            # Create logs directory if it doesn't exist
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            
            # Generate log file name with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file_path = logs_dir / f"anybot_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Prevent propagation to avoid duplicate logs
    logging.getLogger("uvicorn").propagate = False
    logging.getLogger("fastapi").propagate = False
    logging.getLogger("asyncio").propagate = False


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name
    
    Args:
        name: Name of the logger
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Predefined log levels
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


def configure_app_logging():
    """
    Configure logging for the AnyBot application with optimal settings
    """
    setup_logging(
        level=logging.INFO,
        log_to_file=True,
        log_to_console=True
    )


# Convenience functions
def debug(message: str, *args, **kwargs):
    """Log a debug message"""
    logging.debug(message, *args, **kwargs)


def info(message: str, *args, **kwargs):
    """Log an info message"""
    logging.info(message, *args, **kwargs)


def warning(message: str, *args, **kwargs):
    """Log a warning message"""
    logging.warning(message, *args, **kwargs)


def error(message: str, *args, **kwargs):
    """Log an error message"""
    logging.error(message, *args, **kwargs)


def critical(message: str, *args, **kwargs):
    """Log a critical message"""
    logging.critical(message, *args, **kwargs)


def exception(message: str, *args, **kwargs):
    """Log an exception with traceback"""
    logging.exception(message, *args, **kwargs)