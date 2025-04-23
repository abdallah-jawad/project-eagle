import logging
import sys

def setup_logging():
    """Configure logging for the entire application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Create logger for the application
    logger = logging.getLogger('computer_vision')
    return logger 