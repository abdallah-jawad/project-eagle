import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def setup_cuda_environment():
    """
    Set up CUDA environment variables and paths for ONNX Runtime GPU acceleration.
    This should be called before initializing any ONNX Runtime sessions.
    """
    try:
        # Define CUDA and cuDNN paths
        cuda_path = Path("C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.9")
        cudnn_path = Path("C:/Program Files/NVIDIA/CUDNN/v9.9/bin/12.9")
        
        # Verify paths exist
        if not cuda_path.exists():
            raise FileNotFoundError(f"CUDA path not found: {cuda_path}")
        if not cudnn_path.exists():
            raise FileNotFoundError(f"cuDNN path not found: {cudnn_path}")
            
        # Add paths to environment
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + str(cuda_path / "bin")
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + str(cudnn_path)
        
        # Set CUDA_VISIBLE_DEVICES to ensure GPU is used
        os.environ['CUDA_VISIBLE_DEVICES'] = '0'
        
        logger.info("CUDA environment setup completed successfully")
        logger.info(f"Added to PATH: {cuda_path / 'bin'}")
        logger.info(f"Added to PATH: {cudnn_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to set up CUDA environment: {str(e)}")
        return False

if __name__ == "__main__":
    # Set up logging for testing
    logging.basicConfig(level=logging.INFO)
    setup_cuda_environment() 