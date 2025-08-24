import cv2
import numpy as np
import mediapipe as mp
import os
from video_processor import VideoProcessor
import face_recognition
from PIL import Image, ImageEnhance, ImageFilter
import dlib

class MakeupTransformer:
    def __init__(self):
        # Initialize MediaPipe face detection
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize face detection models
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.video_processor = VideoProcessor()
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Define makeup transformation parameters
        self.american_makeup_style = {
            'skin_tone_adjustment': 0.15,  # Lighter skin tone
            'eye_enhancement': 1.3,        # More prominent eyes
            'lip_color': (180, 100, 120),  # Natural pink lips
            'cheek_enhancement': 1.2,      # Subtle contouring
            'eyebrow_definition': 1.1,     # Defined eyebrows
            'overall_brightness': 1.1      # Brighter overall look
        }
    
    def transform_video(self, video_path, job_id):
        """Transform makeup style in entire video"""
        try:
            # Extract frames from video
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            transformed_frames = []
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Transform makeup in current frame
                transformed_frame = self.transform_frame_makeup(frame)
                transformed_frames.append(transformed_frame)
                
                frame_count += 1
                if frame_count % 30 == 0:  # Log progress every 30 frames
                    print(f"Processed {frame_count} frames...")
            
            cap.release()
            
            # Convert frames back to video
            output_path = os.path.join(self.temp_dir, f"transformed_video_{job_id}.mp4")
            self.video_processor.frames_to_video(transformed_frames, output_path, fps)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Error transforming video: {str(e)}")
    
    def transform_frame_makeup(self, frame):
        """Transform makeup style in a single frame"""
        try:
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces and landmarks
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    # Apply makeup transformation
                    frame = self.apply_american_makeup_style(frame, face_landmarks)
            
            return frame
            
        except Exception as e:
            print(f"Error transforming frame: {str(e)}")
            return frame  # Return original frame if transformation fails
    
    def apply_american_makeup_style(self, frame, face_landmarks):
        """Apply American mainstream makeup style to detected face"""
        try:
            h, w, _ = frame.shape
            
            # Convert landmarks to pixel coordinates
            landmarks = []
            for landmark in face_landmarks.landmark:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                landmarks.append((x, y))
            
            # Apply various makeup transformations
            frame = self.adjust_skin_tone(frame, landmarks)
            frame = self.enhance_eyes(frame, landmarks)
            frame = self.apply_lip_color(frame, landmarks)
            frame = self.enhance_cheeks(frame, landmarks)
            frame = self.define_eyebrows(frame, landmarks)
            frame = self.adjust_overall_brightness(frame, landmarks)
            
            return frame
            
        except Exception as e:
            print(f"Error applying makeup: {str(e)}")
            return frame
    
    def adjust_skin_tone(self, frame, landmarks):
        """Adjust skin tone to appear more mainstream American"""
        try:
            # Create face mask
            face_mask = self.create_face_mask(frame, landmarks)
            
            # Convert to LAB color space for better skin tone adjustment
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Lighten the L channel (lightness) slightly
            l = cv2.add(l, int(self.american_makeup_style['skin_tone_adjustment'] * 255))
            
            # Reduce yellow tones (adjust b channel)
            b = cv2.subtract(b, 5)
            
            # Merge channels back
            lab_adjusted = cv2.merge([l, a, b])
            adjusted = cv2.cvtColor(lab_adjusted, cv2.COLOR_LAB2BGR)
            
            # Apply only to face region
            result = np.where(face_mask[..., np.newaxis], adjusted, frame)
            
            return result.astype(np.uint8)
            
        except Exception as e:
            print(f"Error adjusting skin tone: {str(e)}")
            return frame
    
    def enhance_eyes(self, frame, landmarks):
        """Enhance eyes with American makeup style"""
        try:
            # Get eye regions
            left_eye_points = self.get_eye_landmarks(landmarks, 'left')
            right_eye_points = self.get_eye_landmarks(landmarks, 'right')
            
            # Enhance each eye
            frame = self.enhance_single_eye(frame, left_eye_points)
            frame = self.enhance_single_eye(frame, right_eye_points)
            
            return frame
            
        except Exception as e:
            print(f"Error enhancing eyes: {str(e)}")
            return frame
    
    def enhance_single_eye(self, frame, eye_points):
        """Enhance a single eye"""
        if not eye_points:
            return frame
        
        try:
            # Create eye mask
            mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            cv2.fillPoly(mask, [np.array(eye_points)], 255)
            
            # Enhance eye region
            enhanced = cv2.addWeighted(frame, 1.0, frame, 
                                     self.american_makeup_style['eye_enhancement'] - 1.0, 0)
            
            # Apply enhancement only to eye region
            result = np.where(mask[..., np.newaxis], enhanced, frame)
            
            return result.astype(np.uint8)
            
        except Exception as e:
            return frame
    
    def apply_lip_color(self, frame, landmarks):
        """Apply natural pink lip color"""
        try:
            # Get lip landmarks
            lip_points = self.get_lip_landmarks(landmarks)
            
            if lip_points:
                # Create lip mask
                mask = np.zeros(frame.shape[:2], dtype=np.uint8)
                cv2.fillPoly(mask, [np.array(lip_points)], 255)
                
                # Create colored overlay
                overlay = frame.copy()
                lip_color = self.american_makeup_style['lip_color']
                overlay[mask > 0] = lip_color
                
                # Blend with original
                alpha = 0.3  # Transparency for natural look
                result = cv2.addWeighted(frame, 1-alpha, overlay, alpha, 0)
                
                return result
            
            return frame
            
        except Exception as e:
            print(f"Error applying lip color: {str(e)}")
            return frame
    
    def enhance_cheeks(self, frame, landmarks):
        """Add subtle cheek enhancement/contouring"""
        try:
            # Get cheek regions
            left_cheek = self.get_cheek_landmarks(landmarks, 'left')
            right_cheek = self.get_cheek_landmarks(landmarks, 'right')
            
            # Enhance cheeks
            frame = self.enhance_single_cheek(frame, left_cheek)
            frame = self.enhance_single_cheek(frame, right_cheek)
            
            return frame
            
        except Exception as e:
            print(f"Error enhancing cheeks: {str(e)}")
            return frame
    
    def enhance_single_cheek(self, frame, cheek_points):
        """Enhance a single cheek"""
        if not cheek_points:
            return frame
        
        try:
            # Create circular gradient for natural cheek enhancement
            center = np.mean(cheek_points, axis=0).astype(int)
            radius = 30
            
            # Create mask with gradient
            mask = np.zeros(frame.shape[:2], dtype=np.float32)
            y, x = np.ogrid[:frame.shape[0], :frame.shape[1]]
            distance = np.sqrt((x - center[0])**2 + (y - center[1])**2)
            mask[distance <= radius] = 1 - (distance[distance <= radius] / radius)
            
            # Apply subtle pink enhancement
            enhanced = frame.copy().astype(np.float32)
            enhancement_factor = self.american_makeup_style['cheek_enhancement']
            enhanced[:, :, 2] = enhanced[:, :, 2] * (1 + mask * (enhancement_factor - 1) * 0.1)  # Red channel
            enhanced[:, :, 1] = enhanced[:, :, 1] * (1 + mask * (enhancement_factor - 1) * 0.05)  # Green channel
            
            return np.clip(enhanced, 0, 255).astype(np.uint8)
            
        except Exception as e:
            return frame
    
    def define_eyebrows(self, frame, landmarks):
        """Define eyebrows for American makeup style"""
        try:
            # Get eyebrow landmarks
            left_eyebrow = self.get_eyebrow_landmarks(landmarks, 'left')
            right_eyebrow = self.get_eyebrow_landmarks(landmarks, 'right')
            
            # Enhance eyebrows
            frame = self.enhance_single_eyebrow(frame, left_eyebrow)
            frame = self.enhance_single_eyebrow(frame, right_eyebrow)
            
            return frame
            
        except Exception as e:
            print(f"Error defining eyebrows: {str(e)}")
            return frame
    
    def enhance_single_eyebrow(self, frame, eyebrow_points):
        """Enhance a single eyebrow"""
        if not eyebrow_points:
            return frame
        
        try:
            # Draw slightly thicker, more defined eyebrow
            pts = np.array(eyebrow_points, np.int32)
            cv2.polylines(frame, [pts], False, (80, 60, 40), 2)  # Brown color
            
            return frame
            
        except Exception as e:
            return frame
    
    def adjust_overall_brightness(self, frame, landmarks):
        """Adjust overall brightness for American mainstream look"""
        try:
            # Create face mask
            face_mask = self.create_face_mask(frame, landmarks)
            
            # Brighten the face region slightly
            brightened = cv2.convertScaleAbs(frame, alpha=self.american_makeup_style['overall_brightness'], beta=10)
            
            # Apply only to face region
            result = np.where(face_mask[..., np.newaxis], brightened, frame)
            
            return result.astype(np.uint8)
            
        except Exception as e:
            print(f"Error adjusting brightness: {str(e)}")
            return frame
    
    def create_face_mask(self, frame, landmarks):
        """Create a mask for the face region"""
        try:
            mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            
            # Use face contour landmarks to create mask
            face_contour = landmarks[0:17] + landmarks[78:109]  # Approximate face contour
            face_contour = np.array(face_contour, dtype=np.int32)
            
            cv2.fillPoly(mask, [face_contour], 255)
            
            # Smooth the mask
            mask = cv2.GaussianBlur(mask, (21, 21), 0)
            
            return mask > 0
            
        except Exception as e:
            return np.ones(frame.shape[:2], dtype=bool)
    
    def get_eye_landmarks(self, landmarks, side):
        """Get landmarks for left or right eye"""
        try:
            if side == 'left':
                # Left eye landmarks (from MediaPipe face mesh)
                eye_indices = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
            else:
                # Right eye landmarks
                eye_indices = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
            
            return [landmarks[i] for i in eye_indices if i < len(landmarks)]
            
        except Exception as e:
            return []
    
    def get_lip_landmarks(self, landmarks):
        """Get landmarks for lips"""
        try:
            # Lip landmarks from MediaPipe face mesh
            lip_indices = [61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318]
            return [landmarks[i] for i in lip_indices if i < len(landmarks)]
            
        except Exception as e:
            return []
    
    def get_cheek_landmarks(self, landmarks, side):
        """Get approximate cheek landmarks"""
        try:
            if side == 'left':
                # Approximate left cheek area
                cheek_indices = [116, 117, 118, 119, 120, 121, 126, 142, 36, 205, 206, 207, 213, 192, 147]
            else:
                # Approximate right cheek area
                cheek_indices = [345, 346, 347, 348, 349, 350, 451, 452, 453, 464, 435, 410, 454]
            
            return [landmarks[i] for i in cheek_indices if i < len(landmarks)]
            
        except Exception as e:
            return []
    
    def get_eyebrow_landmarks(self, landmarks, side):
        """Get landmarks for eyebrows"""
        try:
            if side == 'left':
                # Left eyebrow landmarks
                eyebrow_indices = [46, 53, 52, 51, 48, 115, 131, 134, 102, 48, 64]
            else:
                # Right eyebrow landmarks  
                eyebrow_indices = [276, 283, 282, 281, 278, 344, 360, 363, 331, 278, 294]
            
            return [landmarks[i] for i in eyebrow_indices if i < len(landmarks)]
            
        except Exception as e:
            return []