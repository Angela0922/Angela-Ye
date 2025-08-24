#!/usr/bin/env python3
"""
Download required models and dependencies for TikTok Video Translator & Makeup Transformer.
"""

import os
import sys
import requests
import zipfile
import tarfile
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model URLs and configurations
MODELS = {
    'face_detection': {
        'url': 'https://github.com/opencv/opencv/raw/master/data/haarcascades/haarcascade_frontalface_default.xml',
        'filename': 'haarcascade_frontalface_default.xml',
        'type': 'file'
    },
    'mediapipe_models': {
        'url': 'https://storage.googleapis.com/mediapipe-models/face_detection/blaze_face_short_range/float16/1/blaze_face_short_range.tflite',
        'filename': 'blaze_face_short_range.tflite',
        'type': 'file'
    },
    'makeup_style_transfer': {
        'url': 'https://example.com/makeup_style_transfer.pth',  # Placeholder URL
        'filename': 'makeup_style_transfer.pth',
        'type': 'file'
    }
}

def download_file(url: str, filename: str, models_dir: Path) -> bool:
    """
    Download a file from URL.
    
    Args:
        url: URL to download from
        filename: Name to save the file as
        models_dir: Directory to save the file in
        
    Returns:
        True if successful, False otherwise
    """
    filepath = models_dir / filename
    
    try:
        logger.info(f"Downloading {filename} from {url}")
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Progress indicator
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        sys.stdout.write(f"\rDownloading {filename}: {progress:.1f}%")
                        sys.stdout.flush()
        
        sys.stdout.write("\n")
        logger.info(f"Successfully downloaded {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Error downloading {filename}: {e}")
        if filepath.exists():
            filepath.unlink()
        return False

def extract_archive(archive_path: Path, extract_dir: Path) -> bool:
    """
    Extract a compressed archive.
    
    Args:
        archive_path: Path to the archive file
        extract_dir: Directory to extract to
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Extracting {archive_path.name}")
        
        if archive_path.suffix == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        elif archive_path.suffix in ['.tar', '.tar.gz', '.tgz']:
            with tarfile.open(archive_path, 'r:*') as tar_ref:
                tar_ref.extractall(extract_dir)
        else:
            logger.warning(f"Unknown archive format: {archive_path.suffix}")
            return False
        
        logger.info(f"Successfully extracted {archive_path.name}")
        return True
        
    except Exception as e:
        logger.error(f"Error extracting {archive_path.name}: {e}")
        return False

def setup_directories() -> Path:
    """
    Create necessary directories for models and data.
    
    Returns:
        Path to models directory
    """
    # Create directories
    models_dir = Path("models")
    data_dir = Path("data")
    output_dir = Path("output")
    
    for directory in [models_dir, data_dir, output_dir]:
        directory.mkdir(exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    return models_dir

def download_models(models_dir: Path) -> bool:
    """
    Download all required models.
    
    Args:
        models_dir: Directory to save models in
        
    Returns:
        True if all downloads successful, False otherwise
    """
    success_count = 0
    total_count = len(MODELS)
    
    for model_name, model_info in MODELS.items():
        logger.info(f"Processing model: {model_name}")
        
        if model_info['type'] == 'file':
            success = download_file(
                model_info['url'],
                model_info['filename'],
                models_dir
            )
            if success:
                success_count += 1
        else:
            logger.warning(f"Unknown model type: {model_info['type']}")
    
    logger.info(f"Downloaded {success_count}/{total_count} models successfully")
    return success_count == total_count

def install_dependencies():
    """Install Python dependencies."""
    logger.info("Installing Python dependencies...")
    
    try:
        import subprocess
        import sys
        
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logger.info("Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing dependencies: {e}")
        return False

def verify_installation():
    """Verify that all components are properly installed."""
    logger.info("Verifying installation...")
    
    # Check if required directories exist
    required_dirs = ["models", "data", "output"]
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            logger.error(f"Missing directory: {dir_name}")
            return False
    
    # Check if required models exist
    models_dir = Path("models")
    for model_name, model_info in MODELS.items():
        model_file = models_dir / model_info['filename']
        if not model_file.exists():
            logger.warning(f"Missing model file: {model_file}")
    
    # Test imports
    try:
        import cv2
        import mediapipe as mp
        import torch
        import numpy as np
        from PIL import Image
        logger.info("All required packages imported successfully")
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return False
    
    logger.info("Installation verification complete")
    return True

def main():
    """Main function to download models and setup the environment."""
    
    print("🚀 TikTok Video Translator & Makeup Transformer - Model Downloader")
    print("=" * 70)
    
    # Setup directories
    logger.info("Setting up directories...")
    models_dir = setup_directories()
    
    # Install dependencies
    logger.info("Installing Python dependencies...")
    if not install_dependencies():
        logger.error("Failed to install dependencies")
        sys.exit(1)
    
    # Download models
    logger.info("Downloading AI models...")
    if not download_models(models_dir):
        logger.warning("Some models failed to download. The application may not work optimally.")
    
    # Verify installation
    logger.info("Verifying installation...")
    if not verify_installation():
        logger.error("Installation verification failed")
        sys.exit(1)
    
    print("\n✅ Setup complete!")
    print("\nYou can now run the application:")
    print("  • Web interface: streamlit run app.py")
    print("  • Command line: python main.py --input video.mp4")
    print("\nFor more information, see the README.md file.")

if __name__ == "__main__":
    main()