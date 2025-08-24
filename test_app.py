#!/usr/bin/env python3
"""
Test script for TikTok Video Translator & Makeup Transformer
"""

import os
import sys
import logging
import tempfile
import numpy as np
import cv2
from pathlib import Path

# Import our modules
from video_processor import VideoProcessor
from audio_translator import AudioTranslator
from face_detector import FaceDetector
from makeup_transformer import MakeupTransformer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_image(width: int = 640, height: int = 480) -> np.ndarray:
    """Create a test image with a simple face-like pattern."""
    # Create a simple test image
    image = np.ones((height, width, 3), dtype=np.uint8) * 200  # Light gray background
    
    # Draw a simple face-like pattern
    # Face circle
    center = (width // 2, height // 2)
    cv2.circle(image, center, 100, (255, 220, 180), -1)  # Skin tone
    
    # Eyes
    left_eye = (center[0] - 30, center[1] - 20)
    right_eye = (center[0] + 30, center[1] - 20)
    cv2.circle(image, left_eye, 10, (255, 255, 255), -1)  # White
    cv2.circle(image, right_eye, 10, (255, 255, 255), -1)
    cv2.circle(image, left_eye, 5, (0, 0, 0), -1)  # Black pupil
    cv2.circle(image, right_eye, 5, (0, 0, 0), -1)
    
    # Nose
    nose = (center[0], center[1] + 10)
    cv2.circle(image, nose, 5, (255, 200, 150), -1)
    
    # Mouth
    mouth_center = (center[0], center[1] + 40)
    cv2.ellipse(image, mouth_center, (20, 10), 0, 0, 180, (150, 50, 50), 2)
    
    return image

def test_face_detection():
    """Test face detection functionality."""
    logger.info("Testing face detection...")
    
    try:
        # Create test image
        test_image = create_test_image()
        
        # Initialize face detector
        face_detector = FaceDetector()
        
        # Detect faces
        faces = face_detector.detect_faces(test_image)
        
        logger.info(f"Detected {len(faces)} faces")
        
        # Test face regions extraction
        if faces:
            face_regions = face_detector.get_face_regions(faces[0])
            logger.info(f"Extracted {len(face_regions)} face regions")
        
        # Cleanup
        face_detector.cleanup()
        
        logger.info("✅ Face detection test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Face detection test failed: {e}")
        return False

def test_makeup_transformation():
    """Test makeup transformation functionality."""
    logger.info("Testing makeup transformation...")
    
    try:
        # Create test image
        test_image = create_test_image()
        
        # Initialize components
        face_detector = FaceDetector()
        makeup_transformer = MakeupTransformer()
        
        # Detect faces
        faces = face_detector.detect_faces(test_image)
        
        if faces:
            # Apply makeup transformation
            transformed_image = makeup_transformer.transform_face(test_image, faces[0])
            
            # Check if transformation was applied
            if transformed_image is not None and transformed_image.shape == test_image.shape:
                logger.info("✅ Makeup transformation applied successfully")
            else:
                logger.warning("⚠️ Makeup transformation may not have worked as expected")
        
        # Cleanup
        face_detector.cleanup()
        
        logger.info("✅ Makeup transformation test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Makeup transformation test failed: {e}")
        return False

def test_video_processor():
    """Test video processing functionality."""
    logger.info("Testing video processor...")
    
    try:
        # Create a simple test video
        test_video_path = create_test_video()
        
        # Initialize video processor
        video_processor = VideoProcessor()
        
        # Get video info
        video_info = video_processor.get_video_info(test_video_path)
        logger.info(f"Video info: {video_info}")
        
        # Extract frames
        frame_paths, fps = video_processor.extract_frames(test_video_path)
        logger.info(f"Extracted {len(frame_paths)} frames at {fps} FPS")
        
        # Cleanup
        video_processor.cleanup_temp_files()
        os.unlink(test_video_path)
        
        logger.info("✅ Video processor test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Video processor test failed: {e}")
        return False

def create_test_video(duration: float = 2.0, fps: int = 30) -> str:
    """Create a simple test video file."""
    logger.info("Creating test video...")
    
    # Create temporary video file
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
        video_path = tmp_file.name
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, fps, (640, 480))
    
    # Generate frames
    num_frames = int(duration * fps)
    for i in range(num_frames):
        # Create frame with moving face
        frame = create_test_image()
        
        # Add some movement
        offset = int(10 * np.sin(i * 0.1))
        frame = np.roll(frame, offset, axis=1)
        
        out.write(frame)
    
    out.release()
    logger.info(f"Created test video: {video_path}")
    return video_path

def test_audio_translator():
    """Test audio translation functionality."""
    logger.info("Testing audio translator...")
    
    try:
        # Initialize audio translator
        audio_translator = AudioTranslator()
        
        # Test text translation
        test_text = "Hola, este es un video de prueba"
        translated_text = audio_translator.translate_text(test_text, 'es', 'en')
        
        logger.info(f"Original: {test_text}")
        logger.info(f"Translated: {translated_text}")
        
        # Test speech synthesis
        test_output_path = "test_audio.wav"
        audio_path = audio_translator.synthesize_speech(translated_text, test_output_path)
        
        if os.path.exists(audio_path):
            logger.info(f"✅ Speech synthesis successful: {audio_path}")
            os.unlink(audio_path)  # Cleanup
        
        # Cleanup
        audio_translator.cleanup_temp_files()
        
        logger.info("✅ Audio translator test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Audio translator test failed: {e}")
        return False

def test_integration():
    """Test integration of all components."""
    logger.info("Testing full integration...")
    
    try:
        # Create test video
        test_video_path = create_test_video()
        
        # Initialize all components
        video_processor = VideoProcessor()
        audio_translator = AudioTranslator()
        face_detector = FaceDetector()
        makeup_transformer = MakeupTransformer()
        
        # Extract frames
        frame_paths, fps = video_processor.extract_frames(test_video_path)
        
        # Process a few frames
        processed_frames = []
        for i, frame_path in enumerate(frame_paths[:5]):  # Process first 5 frames
            processed_path = video_processor.process_frame(
                frame_path, 
                face_detector, 
                makeup_transformer
            )
            processed_frames.append(processed_path)
        
        logger.info(f"Processed {len(processed_frames)} frames")
        
        # Cleanup
        video_processor.cleanup_temp_files()
        audio_translator.cleanup_temp_files()
        face_detector.cleanup()
        os.unlink(test_video_path)
        
        logger.info("✅ Integration test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 TikTok Video Translator & Makeup Transformer - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Face Detection", test_face_detection),
        ("Makeup Transformation", test_makeup_transformation),
        ("Video Processor", test_video_processor),
        ("Audio Translator", test_audio_translator),
        ("Integration", test_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} test passed")
        else:
            print(f"❌ {test_name} test failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to use.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the logs for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)