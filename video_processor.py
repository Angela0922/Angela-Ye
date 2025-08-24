import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
import os
from typing import List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoProcessor:
    """Handles video processing operations including frame extraction and reconstruction."""
    
    def __init__(self, fps: int = 30):
        self.fps = fps
        self.temp_dir = "temp_frames"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def extract_frames(self, video_path: str) -> Tuple[List[str], float]:
        """
        Extract frames from video and save them as images.
        
        Args:
            video_path: Path to input video file
            
        Returns:
            Tuple of (frame_paths, original_fps)
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        original_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_paths = []
        
        logger.info(f"Extracting {frame_count} frames from video...")
        
        for i in range(frame_count):
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_path = os.path.join(self.temp_dir, f"frame_{i:06d}.jpg")
            cv2.imwrite(frame_path, frame)
            frame_paths.append(frame_path)
            
            if i % 100 == 0:
                logger.info(f"Processed {i}/{frame_count} frames")
        
        cap.release()
        logger.info(f"Successfully extracted {len(frame_paths)} frames")
        return frame_paths, original_fps
    
    def process_frame(self, frame_path: str, face_detector, makeup_transformer) -> str:
        """
        Process a single frame with face detection and makeup transformation.
        
        Args:
            frame_path: Path to input frame
            face_detector: Face detection instance
            makeup_transformer: Makeup transformation instance
            
        Returns:
            Path to processed frame
        """
        frame = cv2.imread(frame_path)
        if frame is None:
            return frame_path
        
        # Detect faces
        faces = face_detector.detect_faces(frame)
        
        # Apply makeup transformation to each face
        for face in faces:
            frame = makeup_transformer.transform_face(frame, face)
        
        # Save processed frame
        processed_path = frame_path.replace('.jpg', '_processed.jpg')
        cv2.imwrite(processed_path, frame)
        return processed_path
    
    def reconstruct_video(self, frame_paths: List[str], audio_path: str, 
                         output_path: str, fps: float) -> str:
        """
        Reconstruct video from processed frames and translated audio.
        
        Args:
            frame_paths: List of paths to processed frames
            audio_path: Path to translated audio file
            output_path: Path for output video
            fps: Frames per second for output video
            
        Returns:
            Path to output video
        """
        logger.info("Reconstructing video...")
        
        # Create video from frames
        if not frame_paths:
            raise ValueError("No frames provided for video reconstruction")
        
        # Use first frame to get dimensions
        first_frame = cv2.imread(frame_paths[0])
        height, width = first_frame.shape[:2]
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        for frame_path in frame_paths:
            frame = cv2.imread(frame_path)
            if frame is not None:
                out.write(frame)
        
        out.release()
        
        # Combine video with audio using moviepy
        video_clip = VideoFileClip(output_path)
        audio_clip = AudioFileClip(audio_path)
        
        # Ensure audio duration matches video
        if audio_clip.duration > video_clip.duration:
            audio_clip = audio_clip.subclip(0, video_clip.duration)
        elif audio_clip.duration < video_clip.duration:
            # Loop audio if it's shorter than video
            loops_needed = int(video_clip.duration / audio_clip.duration) + 1
            audio_clip = audio_clip.loop(loops_needed).subclip(0, video_clip.duration)
        
        final_clip = video_clip.set_audio(audio_clip)
        final_output_path = output_path.replace('.mp4', '_with_audio.mp4')
        final_clip.write_videofile(final_output_path, codec='libx264', audio_codec='aac')
        
        # Clean up
        video_clip.close()
        audio_clip.close()
        final_clip.close()
        
        # Remove temporary video without audio
        os.remove(output_path)
        
        logger.info(f"Video reconstruction complete: {final_output_path}")
        return final_output_path
    
    def cleanup_temp_files(self):
        """Clean up temporary frame files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            logger.info("Cleaned up temporary files")
    
    def get_video_info(self, video_path: str) -> dict:
        """
        Get video information including duration, resolution, and fps.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video information
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        return {
            'fps': fps,
            'frame_count': frame_count,
            'width': width,
            'height': height,
            'duration': duration
        }