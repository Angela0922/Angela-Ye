from typing import Tuple
import cv2
import numpy as np
import mediapipe as mp
from tqdm import tqdm


_FACE_MESH = mp.solutions.face_mesh.FaceMesh(static_image_mode=False, max_num_faces=4, refine_landmarks=True)


def _overlay_color_polygon(frame: np.ndarray, points: np.ndarray, color_bgr: Tuple[int, int, int], alpha: float) -> None:
	mask = np.zeros(frame.shape[:2], dtype=np.uint8)
	cv2.fillPoly(mask, [points.astype(np.int32)], 255)
	color_img = np.full_like(frame, color_bgr, dtype=np.uint8)
	blended = cv2.addWeighted(frame, 1 - alpha, color_img, alpha, 0)
	frame[mask == 255] = blended[mask == 255]


def _smooth_region(frame: np.ndarray, points: np.ndarray, ksize: int = 11, sigma: float = 10.0, alpha: float = 0.4) -> None:
	mask = np.zeros(frame.shape[:2], dtype=np.uint8)
	cv2.fillPoly(mask, [points.astype(np.int32)], 255)
	blurred = cv2.GaussianBlur(frame, (ksize, ksize), sigma)
	frame[mask == 255] = cv2.addWeighted(frame[mask == 255], 1 - alpha, blurred[mask == 255], alpha, 0)


def _landmarks_to_points(landmarks, width: int, height: int) -> np.ndarray:
	pts = []
	for lm in landmarks:
		x = int(lm.x * width)
		y = int(lm.y * height)
		pts.append([x, y])
	return np.array(pts, dtype=np.int32)


def apply_neutral_makeup_to_video(input_video: str, output_video: str, intensity: float = 0.6) -> None:
	"""Apply a neutral, mainstream soft-glam makeup style irrespective of ethnicity.

	- Light skin smoothing on cheeks and forehead
	- Soft pinkish lip tint
	- Mild eyeliner/eyeshadow accent
	- Slight eyebrow darkening
	"""
	cap = cv2.VideoCapture(input_video)
	if not cap.isOpened():
		raise RuntimeError(f"Failed to open video: {input_video}")

	fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
	width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
	height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
	fourcc = cv2.VideoWriter_fourcc(*"mp4v")
	writer = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

	pbar = tqdm(total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or None, desc="Makeup", unit="f")
	try:
		while True:
			ret, frame = cap.read()
			if not ret:
				break

			rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			res = _FACE_MESH.process(rgb)
			if res.multi_face_landmarks:
				for face in res.multi_face_landmarks:
					pts = _landmarks_to_points(face.landmark, width, height)

					# Define regions by MediaPipe indices (approximate groups)
					lips_outer = pts[[61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 415, 310, 311, 312, 13, 82, 81, 42, 183, 78, 95, 88, 178]]
					lips_inner = pts[[78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308, 415, 310, 311, 312, 13, 82, 81, 42, 183]]
					left_eye = pts[[33, 159, 158, 133, 153, 144, 145, 246]]
					right_eye = pts[[362, 386, 385, 263, 373, 380, 374, 466]]
					left_brow = pts[[70, 63, 105, 66, 107]]
					right_brow = pts[[336, 296, 334, 293, 300]]

					# Skin smoothing on cheeks/forehead: use convex hull of cheeks and forehead landmarks (approximate)
					face_hull = cv2.convexHull(pts)
					_smooth_region(frame, face_hull.reshape(-1, 2), ksize=9, sigma=10.0, alpha=0.15 + 0.25 * intensity)

					# Lips tint (subtle pink)
					lip_color = (180, 105, 155)  # BGR soft rose
					_overlay_color_polygon(frame, lips_outer, lip_color, alpha=0.10 + 0.25 * intensity)
					_overlay_color_polygon(frame, lips_inner, lip_color, alpha=0.10 + 0.25 * intensity)

					# Soft eyeliner/eyeshadow (light brown)
					eye_color = (80, 120, 180)  # BGR light brown-ish tint
					_overlay_color_polygon(frame, left_eye, eye_color, alpha=0.06 + 0.12 * intensity)
					_overlay_color_polygon(frame, right_eye, eye_color, alpha=0.06 + 0.12 * intensity)

					# Eyebrow darkening
					brow_color = (50, 50, 50)
					_overlay_color_polygon(frame, left_brow, brow_color, alpha=0.08 + 0.18 * intensity)
					_overlay_color_polygon(frame, right_brow, brow_color, alpha=0.08 + 0.18 * intensity)

			writer.write(frame)
			pbar.update(1)
	finally:
		pbar.close()
		cap.release()
		writer.release()