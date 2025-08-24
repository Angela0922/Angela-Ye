#!/usr/bin/env python3
"""
TikTok Video Translator & Makeup Transformer
Startup script with environment setup and error handling
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    logger.info(f"Python version: {sys.version}")
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'outputs', 'temp']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"Created directory: {directory}")

def check_environment():
    """Check if .env file exists and has required variables"""
    env_file = Path('.env')
    if not env_file.exists():
        logger.warning(".env file not found. Creating from template...")
        env_example = Path('.env.example')
        if env_example.exists():
            import shutil
            shutil.copy('.env.example', '.env')
            logger.info("Created .env from .env.example")
            logger.warning("Please edit .env file and add your OpenAI API key")
        else:
            logger.error(".env.example not found")
            return False
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check for OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        logger.warning("OpenAI API key not set. Translation will use fallback mode.")
    else:
        logger.info("OpenAI API key found")
    
    return True

def install_dependencies():
    """Install Python dependencies if needed"""
    try:
        import flask
        import cv2
        import mediapipe
        import whisper
        logger.info("All required packages are installed")
        return True
    except ImportError as e:
        logger.warning(f"Missing package: {e.name}")
        logger.info("Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            logger.info("Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            logger.error("Failed to install dependencies")
            return False

def run_application():
    """Run the Flask application"""
    try:
        from app import app
        logger.info("Starting TikTok Video Translator & Makeup Transformer")
        logger.info("Access the application at: http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        return False

def main():
    """Main startup function"""
    logger.info("=" * 60)
    logger.info("TikTok Video Translator & Makeup Transformer")
    logger.info("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Run application
    run_application()

if __name__ == "__main__":
    main()