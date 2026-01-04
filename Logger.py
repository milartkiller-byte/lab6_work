import logging
from functools import wraps
from typing import Type, Optional

def logged(exception: Type[Exception], mode: str = "console", logfile: Optional[str] = "Logged_Messages.txt"):
    """
   Parameterized decorator.
- `exception`: the exception to catch and log
- `mode`: "console" or "file"
- `logfile`: path to the text log file (only for the "file" mode)
    """
    if mode not in ("console", "file"):
        raise ValueError("mode must be 'console' or 'file'")

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            logger = logging.getLogger(func.__name__)
            logger.setLevel(logging.INFO)

            
            logger.handlers = []

            if mode == "file":
                if not logfile:
                    raise ValueError("logfile must be provided for 'file' mode")
                handler = logging.FileHandler(logfile, encoding="utf-8")
            else:
                handler = logging.StreamHandler()

            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            try:
                result = func(self, *args, **kwargs)
                logger.info(f"Successfully executed: {func.__name__}")
                return result
            except exception as e:
                logger.error(f"Exception in {func.__name__}: {e}")
                raise
        return wrapper
    return decorator

