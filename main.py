#!/usr/bin/env python3
"""
TikTok Video Translator & Makeup Transformer
Main application for processing TikTok videos from Spanish to English with makeup transformation.
"""

import argparse
import os
import sys
import logging
from pathlib import Path
from typing import Optional

# Import our custom modules
from video_processor import VideoProcessor
from audio_translator import AudioTranslator
from face_detector import FaceDetector
from makeup_transformer import MakeupTransformer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tiktok_transformer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TikTokTransformer:
    """Main application class for TikTok video translation and makeup transformation."""
    
    def __init__(self):
        self.video_processor = VideoProcessor()
        self.audio_translator = AudioTranslator()
        self.face_detector = FaceDetector()
        self.makeup_transformer = MakeupTransformer()
        
        # Create output directory
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def process_video(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Process a TikTok video: translate audio and transform makeup.
        
        Args:
            input_path: Path to input video file
            output_path: Path for output video (optional)
            
        Returns:
            Path to processed video
        """
        logger.info(f"Starting video processing: {input_path}")
        
        # Validate input file
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input video not found: {input_path}")
        
        # Generate output path if not provided
        if output_path is None:
            input_name = Path(input_path).stem
            output_path = str(self.output_dir / f"{input_name}_translated.mp4")
        
        try:
            # Step 1: Get video information
            video_info = self.video_processor.get_video_info(input_path)
            logger.info(f"Video info: {video_info}")
            
            # Step 2: Extract frames
            logger.info("Extracting video frames...")
            frame_paths, original_fps = self.video_processor.extract_frames(input_path)
            
            # Step 3: Process audio (extract, transcribe, translate, synthesize)
            logger.info("Processing audio...")
            audio_output_path = str(self.output_dir / "translated_audio.wav")
            translated_audio_path = self.audio_translator.process_audio(input_path, audio_output_path)
            
            # Step 4: Process frames with face detection and makeup transformation
            logger.info("Processing video frames...")
            processed_frame_paths = []
            
            for i, frame_path in enumerate(frame_paths):
                logger.info(f"Processing frame {i+1}/{len(frame_paths)}")
                
                # Process frame
                processed_path = self.video_processor.process_frame(
                    frame_path, 
                    self.face_detector, 
                    self.makeup_transformer
                )
                processed_frame_paths.append(processed_path)
                
                # Progress update
                if (i + 1) % 50 == 0:
                    logger.info(f"Processed {i+1}/{len(frame_paths)} frames")
            
            # Step 5: Reconstruct video with translated audio
            logger.info("Reconstructing video...")
            final_video_path = self.video_processor.reconstruct_video(
                processed_frame_paths,
                translated_audio_path,
                output_path,
                original_fps
            )
            
            logger.info(f"Video processing complete: {final_video_path}")
            return final_video_path
            
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            raise
        finally:
            # Cleanup temporary files
            self.cleanup()
    
    def process_video_batch(self, input_dir: str, output_dir: Optional[str] = None) -> list:
        """
        Process multiple videos in a directory.
        
        Args:
            input_dir: Directory containing input videos
            output_dir: Directory for output videos (optional)
            
        Returns:
            List of processed video paths
        """
        if output_dir is None:
            output_dir = str(self.output_dir)
        
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Find video files
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
        video_files = [
            f for f in input_path.iterdir() 
            if f.is_file() and f.suffix.lower() in video_extensions
        ]
        
        if not video_files:
            logger.warning(f"No video files found in {input_dir}")
            return []
        
        logger.info(f"Found {len(video_files)} video files to process")
        
        processed_videos = []
        
        for video_file in video_files:
            try:
                logger.info(f"Processing {video_file.name}")
                output_file = output_path / f"{video_file.stem}_translated{video_file.suffix}"
                
                processed_path = self.process_video(str(video_file), str(output_file))
                processed_videos.append(processed_path)
                
            except Exception as e:
                logger.error(f"Error processing {video_file.name}: {e}")
                continue
        
        logger.info(f"Batch processing complete. {len(processed_videos)} videos processed successfully.")
        return processed_videos
    
    def cleanup(self):
        """Clean up temporary files and resources."""
        logger.info("Cleaning up temporary files...")
        
        try:
            self.video_processor.cleanup_temp_files()
            self.audio_translator.cleanup_temp_files()
            self.face_detector.cleanup()
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")

def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description="TikTok Video Translator & Makeup Transformer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --input video.mp4 --output translated_video.mp4
  python main.py --input-dir videos/ --output-dir processed/
  python main.py --input video.mp4  # Uses default output path
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        help='Input video file path'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output video file path (optional)'
    )
    
    parser.add_argument(
        '--input-dir',
        type=str,
        help='Input directory containing videos (for batch processing)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory for processed videos (for batch processing)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate arguments
    if not args.input and not args.input_dir:
        parser.error("Either --input or --input-dir must be specified")
    
    if args.input and args.input_dir:
        parser.error("Cannot specify both --input and --input-dir")
    
    try:
        # Initialize transformer
        transformer = TikTokTransformer()
        
        if args.input:
            # Process single video
            processed_path = transformer.process_video(args.input, args.output)
            print(f"✅ Video processed successfully: {processed_path}")
            
        elif args.input_dir:
            # Process batch of videos
            processed_videos = transformer.process_video_batch(args.input_dir, args.output_dir)
            print(f"✅ Batch processing complete. {len(processed_videos)} videos processed.")
            for video in processed_videos:
                print(f"  - {video}")
        
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()