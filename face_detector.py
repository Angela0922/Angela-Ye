import cv2
import mediapipe as mp
import numpy as np
from typing import List, Tuple, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceDetector:
    """Handles face detection and landmark extraction using MediaPipe."""
    
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize face detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # 0 for short-range, 1 for full-range
            min_detection_confidence=0.5
        )
        
        # Initialize face mesh for detailed landmarks
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=10,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    
    def detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect faces in the image and extract landmarks.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            List of face dictionaries with bounding boxes and landmarks
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        detection_results = self.face_detection.process(rgb_image)
        mesh_results = self.face_mesh.process(rgb_image)
        
        faces = []
        height, width = image.shape[:2]
        
        if detection_results.detections:
            for i, detection in enumerate(detection_results.detections):
                face_data = {
                    'bbox': self._get_bounding_box(detection, width, height),
                    'confidence': detection.score[0],
                    'landmarks': self._extract_landmarks(mesh_results, i, width, height),
                    'keypoints': self._extract_keypoints(detection, width, height)
                }
                faces.append(face_data)
        
        return faces
    
    def _get_bounding_box(self, detection, width: int, height: int) -> Tuple[int, int, int, int]:
        """Extract bounding box from detection result."""
        bbox = detection.location_data.relative_bounding_box
        
        x = int(bbox.xmin * width)
        y = int(bbox.ymin * height)
        w = int(bbox.width * width)
        h = int(bbox.height * height)
        
        return (x, y, w, h)
    
    def _extract_keypoints(self, detection, width: int, height: int) -> Dict[str, Tuple[int, int]]:
        """Extract key facial points from detection."""
        keypoints = {}
        
        # Extract key facial landmarks
        landmarks = detection.location_data.relative_keypoints
        
        if len(landmarks) >= 6:
            keypoints['nose'] = (int(landmarks[2].x * width), int(landmarks[2].y * height))
            keypoints['left_eye'] = (int(landmarks[1].x * width), int(landmarks[1].y * height))
            keypoints['right_eye'] = (int(landmarks[0].x * width), int(landmarks[0].y * height))
            keypoints['left_ear'] = (int(landmarks[3].x * width), int(landmarks[3].y * height))
            keypoints['right_ear'] = (int(landmarks[4].x * width), int(landmarks[4].y * height))
            keypoints['mouth'] = (int(landmarks[5].x * width), int(landmarks[5].y * height))
        
        return keypoints
    
    def _extract_landmarks(self, mesh_results, face_idx: int, width: int, height: int) -> List[Tuple[int, int]]:
        """Extract detailed face mesh landmarks."""
        landmarks = []
        
        if mesh_results.multi_face_landmarks and len(mesh_results.multi_face_landmarks) > face_idx:
            face_landmarks = mesh_results.multi_face_landmarks[face_idx]
            
            for landmark in face_landmarks.landmark:
                x = int(landmark.x * width)
                y = int(landmark.y * height)
                landmarks.append((x, y))
        
        return landmarks
    
    def get_face_regions(self, face_data: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """
        Extract different face regions for makeup application.
        
        Args:
            face_data: Face data dictionary
            
        Returns:
            Dictionary of face regions (eyes, lips, cheeks, etc.)
        """
        x, y, w, h = face_data['bbox']
        landmarks = face_data['landmarks']
        keypoints = face_data['keypoints']
        
        regions = {}
        
        # Extract face regions based on landmarks
        if len(landmarks) >= 468:  # Full face mesh
            # Eyes region
            left_eye_landmarks = landmarks[33:46]  # Left eye landmarks
            right_eye_landmarks = landmarks[362:375]  # Right eye landmarks
            
            # Lips region
            lips_landmarks = landmarks[61:85]  # Outer lips
            
            # Cheeks region
            left_cheek_landmarks = landmarks[123:137]  # Left cheek
            right_cheek_landmarks = landmarks[352:366]  # Right cheek
            
            # Create region masks
            regions['left_eye'] = self._create_region_mask(landmarks, left_eye_landmarks)
            regions['right_eye'] = self._create_region_mask(landmarks, right_eye_landmarks)
            regions['lips'] = self._create_region_mask(landmarks, lips_landmarks)
            regions['left_cheek'] = self._create_region_mask(landmarks, left_cheek_landmarks)
            regions['right_cheek'] = self._create_region_mask(landmarks, right_cheek_landmarks)
        
        return regions
    
    def _create_region_mask(self, all_landmarks: List[Tuple[int, int]], 
                          region_landmarks: List[Tuple[int, int]]) -> np.ndarray:
        """Create a mask for a specific face region."""
        if not region_landmarks:
            return None
        
        # Create convex hull for the region
        points = np.array(region_landmarks, dtype=np.int32)
        hull = cv2.convexHull(points)
        
        # Create mask
        mask = np.zeros((480, 640), dtype=np.uint8)  # Adjust size as needed
        cv2.fillPoly(mask, [hull], 255)
        
        return mask
    
    def draw_faces(self, image: np.ndarray, faces: List[Dict[str, Any]]) -> np.ndarray:
        """
        Draw detected faces and landmarks on the image.
        
        Args:
            image: Input image
            faces: List of detected faces
            
        Returns:
            Image with drawn faces and landmarks
        """
        result_image = image.copy()
        
        for face in faces:
            x, y, w, h = face['bbox']
            
            # Draw bounding box
            cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw keypoints
            for point_name, (px, py) in face['keypoints'].items():
                cv2.circle(result_image, (px, py), 3, (255, 0, 0), -1)
                cv2.putText(result_image, point_name, (px + 5, py - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 1)
        
        return result_image
    
    def get_face_orientation(self, face_data: Dict[str, Any]) -> str:
        """
        Determine face orientation (front, left, right, up, down).
        
        Args:
            face_data: Face data dictionary
            
        Returns:
            Face orientation string
        """
        keypoints = face_data['keypoints']
        
        if 'left_eye' in keypoints and 'right_eye' in keypoints:
            left_eye = keypoints['left_eye']
            right_eye = keypoints['right_eye']
            
            # Calculate eye angle
            eye_angle = np.arctan2(right_eye[1] - left_eye[1], right_eye[0] - left_eye[0])
            eye_angle_deg = np.degrees(eye_angle)
            
            # Determine orientation based on eye angle
            if abs(eye_angle_deg) < 5:
                return "front"
            elif eye_angle_deg > 5:
                return "left"
            else:
                return "right"
        
        return "unknown"
    
    def cleanup(self):
        """Clean up MediaPipe resources."""
        self.face_detection.close()
        self.face_mesh.close()