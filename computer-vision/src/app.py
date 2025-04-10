#!/usr/bin/env python3
"""
Main application module for the Computer Vision service.
"""

import time
import logging
import sys
from typing import NoReturn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def hello_world() -> NoReturn:
    """
    Print 'Hello World' indefinitely with a timestamp.
    
    This function runs in an infinite loop, printing a message every 5 seconds.
    """
    logger.info("Starting Hello World service")
    
    try:
        while True:
            logger.info("Hello World!")
            time.sleep(5)  # Sleep for 5 seconds between messages
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    hello_world() 