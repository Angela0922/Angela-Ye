import cv2
import os
from moviepy.editor import VideoFileClip, AudioFileClip
import numpy as np

class VideoProcessor:
    def __init__(self):
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def extract_audio(self, video_path):
        """Extract audio from video and return audio path and video info"""
        try:
            video = VideoFileClip(video_path)
            
            # Get video information
            video_info = {
                'duration': video.duration,
                'fps': video.fps,
                'size': video.size,
                'has_audio': video.audio is not None
            }
            
            # Extract audio
            if video.audio is not None:
                audio_path = os.path.join(self.temp_dir, f"extracted_audio_{os.path.basename(video_path)}.wav")
                video.audio.write_audiofile(audio_path, verbose=False, logger=None)
                video.close()
                return audio_path, video_info
            else:
                video.close()
                raise Exception("Video has no audio track")
                
        except Exception as e:
            raise Exception(f"Error extracting audio: {str(e)}")
    
    def get_video_frames(self, video_path):
        """Extract frames from video for processing"""
        cap = cv2.VideoCapture(video_path)
        frames = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        
        cap.release()
        return frames
    
    def frames_to_video(self, frames, output_path, fps=30):
        """Convert processed frames back to video"""
        if not frames:
            raise Exception("No frames to process")
        
        height, width, layers = frames[0].shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        for frame in frames:
            out.write(frame)
        
        out.release()
        return output_path
    
    def combine_video_audio(self, video_path, audio_path, job_id):
        """Combine processed video with new audio"""
        try:
            video = VideoFileClip(video_path)
            audio = AudioFileClip(audio_path)
            
            # Adjust audio duration to match video
            if audio.duration > video.duration:
                audio = audio.subclip(0, video.duration)
            elif audio.duration < video.duration:
                # Loop audio if it's shorter than video
                from moviepy.editor import concatenate_audioclips
                loops_needed = int(video.duration / audio.duration) + 1
                audio_list = [audio] * loops_needed
                audio = concatenate_audioclips(audio_list).subclip(0, video.duration)
            
            # Combine video and audio
            final_video = video.set_audio(audio)
            
            output_path = os.path.join("outputs", f"final_video_{job_id}.mp4")
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            video.close()
            audio.close()
            final_video.close()
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Error combining video and audio: {str(e)}")
    
    def resize_frame(self, frame, target_size=(512, 512)):
        """Resize frame for processing while maintaining aspect ratio"""
        h, w = frame.shape[:2]
        target_w, target_h = target_size
        
        # Calculate scaling factor
        scale = min(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize frame
        resized = cv2.resize(frame, (new_w, new_h))
        
        # Create padded frame
        padded = np.zeros((target_h, target_w, 3), dtype=np.uint8)
        y_offset = (target_h - new_h) // 2
        x_offset = (target_w - new_w) // 2
        padded[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        
        return padded, (x_offset, y_offset, new_w, new_h)
    
    def restore_frame_size(self, processed_frame, original_shape, crop_info):
        """Restore processed frame to original size"""
        x_offset, y_offset, crop_w, crop_h = crop_info
        
        # Extract the processed region
        processed_crop = processed_frame[y_offset:y_offset+crop_h, x_offset:x_offset+crop_w]
        
        # Resize back to original dimensions
        original_h, original_w = original_shape[:2]
        restored = cv2.resize(processed_crop, (original_w, original_h))
        
        return restored