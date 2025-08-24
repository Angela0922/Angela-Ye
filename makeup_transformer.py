import cv2
import numpy as np
from typing import Dict, Any, Tuple, List
import logging
from PIL import Image, ImageDraw, ImageFilter
import colorsys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MakeupTransformer:
    """Applies AI-powered makeup transformation from Latino to American mainstream styles."""
    
    def __init__(self):
        # Define makeup color palettes
        self.latino_palette = {
            'foundation': [(180, 150, 120), (200, 170, 140)],  # Warmer, deeper tones
            'blush': [(255, 100, 100), (255, 120, 120)],  # Bright coral/peach
            'lipstick': [(200, 50, 80), (220, 60, 90)],  # Deep reds
            'eyeshadow': [(120, 60, 40), (140, 80, 60)],  # Warm browns
            'eyeliner': [(0, 0, 0), (20, 20, 20)],  # Black
            'highlighter': [(255, 220, 180), (255, 240, 200)]  # Golden
        }
        
        self.american_palette = {
            'foundation': [(220, 200, 180), (240, 220, 200)],  # Cooler, lighter tones
            'blush': [(255, 180, 200), (255, 200, 220)],  # Soft pink
            'lipstick': [(240, 120, 140), (255, 140, 160)],  # Natural pinks
            'eyeshadow': [(180, 160, 140), (200, 180, 160)],  # Neutral taupes
            'eyeliner': [(0, 0, 0), (10, 10, 10)],  # Subtle black
            'highlighter': [(255, 255, 255), (255, 250, 240)]  # Pearl white
        }
        
        # Load pre-trained models for style transfer (placeholder)
        self.style_model = None
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained models for makeup style transfer."""
        # In a real implementation, this would load actual AI models
        # For now, we'll use rule-based transformations
        logger.info("Loading makeup transformation models...")
        
        # Placeholder for actual model loading
        # self.style_model = load_pretrained_model('makeup_style_transfer.pth')
        logger.info("Models loaded successfully")
    
    def transform_face(self, image: np.ndarray, face_data: Dict[str, Any]) -> np.ndarray:
        """
        Apply makeup transformation to a detected face.
        
        Args:
            image: Input image (BGR format)
            face_data: Face detection data
            
        Returns:
            Transformed image
        """
        logger.info("Applying makeup transformation...")
        
        # Convert to RGB for processing
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        
        # Extract face regions
        face_regions = self._extract_face_regions(face_data)
        
        # Apply transformations to each region
        transformed_image = pil_image.copy()
        
        # Foundation/base makeup
        if 'face' in face_regions:
            transformed_image = self._apply_foundation(transformed_image, face_regions['face'])
        
        # Eye makeup
        if 'left_eye' in face_regions:
            transformed_image = self._apply_eye_makeup(transformed_image, face_regions['left_eye'], 'left')
        if 'right_eye' in face_regions:
            transformed_image = self._apply_eye_makeup(transformed_image, face_regions['right_eye'], 'right')
        
        # Lip makeup
        if 'lips' in face_regions:
            transformed_image = self._apply_lip_makeup(transformed_image, face_regions['lips'])
        
        # Blush
        if 'left_cheek' in face_regions:
            transformed_image = self._apply_blush(transformed_image, face_regions['left_cheek'])
        if 'right_cheek' in face_regions:
            transformed_image = self._apply_blush(transformed_image, face_regions['right_cheek'])
        
        # Highlighter
        if 'cheekbones' in face_regions:
            transformed_image = self._apply_highlighter(transformed_image, face_regions['cheekbones'])
        
        # Convert back to BGR
        result_image = cv2.cvtColor(np.array(transformed_image), cv2.COLOR_RGB2BGR)
        
        return result_image
    
    def _extract_face_regions(self, face_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract detailed face regions for makeup application."""
        regions = {}
        landmarks = face_data.get('landmarks', [])
        keypoints = face_data.get('keypoints', {})
        
        if len(landmarks) >= 468:  # Full face mesh
            # Face outline
            face_outline = landmarks[0:17] + landmarks[17:22] + landmarks[22:27] + landmarks[27:31] + landmarks[31:36]
            regions['face'] = {'landmarks': face_outline, 'type': 'outline'}
            
            # Eyes
            left_eye = landmarks[33:46]
            right_eye = landmarks[362:375]
            regions['left_eye'] = {'landmarks': left_eye, 'type': 'eye'}
            regions['right_eye'] = {'landmarks': right_eye, 'type': 'eye'}
            
            # Lips
            outer_lips = landmarks[61:85]
            inner_lips = landmarks[85:93]
            regions['lips'] = {'landmarks': outer_lips, 'inner': inner_lips, 'type': 'lips'}
            
            # Cheeks
            left_cheek = landmarks[123:137]
            right_cheek = landmarks[352:366]
            regions['left_cheek'] = {'landmarks': left_cheek, 'type': 'cheek'}
            regions['right_cheek'] = {'landmarks': right_cheek, 'type': 'cheek'}
            
            # Cheekbones for highlighter
            left_cheekbone = landmarks[137:151]
            right_cheekbone = landmarks[366:380]
            regions['cheekbones'] = {'landmarks': left_cheekbone + right_cheekbone, 'type': 'highlight'}
        
        return regions
    
    def _apply_foundation(self, image: Image.Image, face_region: Dict[str, Any]) -> Image.Image:
        """Apply foundation/base makeup transformation."""
        landmarks = face_region['landmarks']
        
        # Create face mask
        mask = self._create_region_mask(image.size, landmarks)
        
        # Get American foundation color
        foundation_color = self.american_palette['foundation'][0]
        
        # Apply foundation with blending
        foundation_layer = Image.new('RGB', image.size, foundation_color)
        blended = Image.blend(image, foundation_layer, 0.3)  # 30% opacity
        
        # Apply only to face region
        result = image.copy()
        result.paste(blended, mask=mask)
        
        return result
    
    def _apply_eye_makeup(self, image: Image.Image, eye_region: Dict[str, Any], side: str) -> Image.Image:
        """Apply eye makeup transformation."""
        landmarks = eye_region['landmarks']
        
        # Create eye mask
        mask = self._create_region_mask(image.size, landmarks)
        
        # Apply eyeshadow
        eyeshadow_color = self.american_palette['eyeshadow'][0]
        eyeshadow_layer = Image.new('RGB', image.size, eyeshadow_color)
        blended = Image.blend(image, eyeshadow_layer, 0.4)
        
        # Apply eyeliner
        eyeliner_color = self.american_palette['eyeliner'][0]
        eyeliner_mask = self._create_eyeliner_mask(image.size, landmarks)
        eyeliner_layer = Image.new('RGB', image.size, eyeliner_color)
        
        # Combine eyeshadow and eyeliner
        result = image.copy()
        result.paste(blended, mask=mask)
        result.paste(eyeliner_layer, mask=eyeliner_mask)
        
        return result
    
    def _apply_lip_makeup(self, image: Image.Image, lip_region: Dict[str, Any]) -> Image.Image:
        """Apply lip makeup transformation."""
        outer_landmarks = lip_region['landmarks']
        inner_landmarks = lip_region.get('inner', [])
        
        # Create lip masks
        outer_mask = self._create_region_mask(image.size, outer_landmarks)
        inner_mask = self._create_region_mask(image.size, inner_landmarks) if inner_landmarks else None
        
        # Get American lipstick color
        lipstick_color = self.american_palette['lipstick'][0]
        
        # Apply lipstick
        lipstick_layer = Image.new('RGB', image.size, lipstick_color)
        
        # Blend with different intensities for inner and outer lips
        outer_blended = Image.blend(image, lipstick_layer, 0.6)
        inner_blended = Image.blend(image, lipstick_layer, 0.8) if inner_mask else outer_blended
        
        result = image.copy()
        result.paste(outer_blended, mask=outer_mask)
        if inner_mask:
            result.paste(inner_blended, mask=inner_mask)
        
        return result
    
    def _apply_blush(self, image: Image.Image, cheek_region: Dict[str, Any]) -> Image.Image:
        """Apply blush transformation."""
        landmarks = cheek_region['landmarks']
        
        # Create cheek mask
        mask = self._create_region_mask(image.size, landmarks)
        
        # Get American blush color
        blush_color = self.american_palette['blush'][0]
        
        # Apply blush with soft blending
        blush_layer = Image.new('RGB', image.size, blush_color)
        blended = Image.blend(image, blush_layer, 0.25)  # Subtle blush
        
        result = image.copy()
        result.paste(blended, mask=mask)
        
        return result
    
    def _apply_highlighter(self, image: Image.Image, highlight_region: Dict[str, Any]) -> Image.Image:
        """Apply highlighter transformation."""
        landmarks = highlight_region['landmarks']
        
        # Create highlight mask
        mask = self._create_region_mask(image.size, landmarks)
        
        # Get American highlighter color
        highlighter_color = self.american_palette['highlighter'][0]
        
        # Apply highlighter
        highlighter_layer = Image.new('RGB', image.size, highlighter_color)
        blended = Image.blend(image, highlighter_layer, 0.3)
        
        result = image.copy()
        result.paste(blended, mask=mask)
        
        return result
    
    def _create_region_mask(self, image_size: Tuple[int, int], landmarks: List[Tuple[int, int]]) -> Image.Image:
        """Create a mask for a specific face region."""
        mask = Image.new('L', image_size, 0)
        draw = ImageDraw.Draw(mask)
        
        if len(landmarks) >= 3:
            # Create polygon from landmarks
            points = [(int(x), int(y)) for x, y in landmarks]
            draw.polygon(points, fill=255)
        
        # Apply Gaussian blur for smooth edges
        mask = mask.filter(ImageFilter.GaussianBlur(radius=2))
        
        return mask
    
    def _create_eyeliner_mask(self, image_size: Tuple[int, int], eye_landmarks: List[Tuple[int, int]]) -> Image.Image:
        """Create a mask for eyeliner application."""
        mask = Image.new('L', image_size, 0)
        draw = ImageDraw.Draw(mask)
        
        if len(eye_landmarks) >= 6:
            # Create eyeliner along the upper eyelid
            upper_lid = eye_landmarks[:6]  # Upper eyelid landmarks
            points = [(int(x), int(y)) for x, y in upper_lid]
            
            # Draw eyeliner line
            for i in range(len(points) - 1):
                draw.line([points[i], points[i + 1]], fill=255, width=2)
        
        return mask
    
    def adjust_skin_tone(self, image: np.ndarray, face_data: Dict[str, Any]) -> np.ndarray:
        """
        Adjust skin tone to match American mainstream standards.
        
        Args:
            image: Input image
            face_data: Face detection data
            
        Returns:
            Image with adjusted skin tone
        """
        # This is a simplified skin tone adjustment
        # In a real implementation, this would use more sophisticated color correction
        
        x, y, w, h = face_data['bbox']
        face_region = image[y:y+h, x:x+w]
        
        # Convert to LAB color space for better skin tone adjustment
        lab = cv2.cvtColor(face_region, cv2.COLOR_BGR2LAB)
        
        # Adjust L channel (lightness) slightly
        lab[:, :, 0] = cv2.add(lab[:, :, 0], 10)  # Lighten slightly
        
        # Adjust A channel (green-red) for warmer tones
        lab[:, :, 1] = cv2.add(lab[:, :, 1], -5)  # Reduce redness slightly
        
        # Convert back to BGR
        adjusted_face = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # Blend with original
        result = image.copy()
        result[y:y+h, x:x+w] = cv2.addWeighted(face_region, 0.7, adjusted_face, 0.3, 0)
        
        return result
    
    def apply_style_transfer(self, image: np.ndarray, face_data: Dict[str, Any]) -> np.ndarray:
        """
        Apply AI-powered style transfer for makeup transformation.
        
        Args:
            image: Input image
            face_data: Face detection data
            
        Returns:
            Styled image
        """
        # This is a placeholder for actual AI style transfer
        # In a real implementation, this would use a pre-trained neural network
        
        logger.info("Applying AI style transfer...")
        
        # For now, we'll use the rule-based approach
        return self.transform_face(image, face_data)