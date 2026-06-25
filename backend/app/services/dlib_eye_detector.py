"""
Eye detection helper for behavioral analysis.
Extracts eye boxes and pupil positions using FER face detection + anatomical calculations.
Falls back to dlib 68-point landmarks if available.
"""
import cv2
import numpy as np
from typing import Optional, Tuple, Dict
import os

# Try to import dlib (optional)
try:
    import dlib
    DLIB_AVAILABLE = True
    _detector = None
    _predictor = None
except ImportError:
    DLIB_AVAILABLE = False
    print("[dlib_eye_detector] dlib not available, using FER-based eye detection")

def _load_dlib_models():
    """Lazy load dlib models if available"""
    if not DLIB_AVAILABLE:
        return None, None
    
    global _detector, _predictor
    if _detector is None:
        _detector = dlib.get_frontal_face_detector()
        # Try to find the shape predictor model
        model_paths = [
            "eyeDetect/models/shape_predictor_68_face_landmarks.dat",
            "../eyeDetect/models/shape_predictor_68_face_landmarks.dat",
            "../../eyeDetect/models/shape_predictor_68_face_landmarks.dat",
        ]
        for model_path in model_paths:
            if os.path.exists(model_path):
                _predictor = dlib.shape_predictor(model_path)
                print(f"[dlib_eye_detector] Loaded dlib shape predictor from {model_path}")
                break
    return _detector, _predictor

def detect_pupil_simple(eye_region):
    """
    Simplified pupil detection using brightness thresholding.
    Returns pupil center (x, y) relative to eye region.
    """
    if eye_region.size == 0 or eye_region.shape[0] < 5 or eye_region.shape[1] < 5:
        return None
    
    try:
        gray_eye = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray_eye, (5, 5), 0)
        
        # Find darkest point (pupil is darkest part of eye)
        min_val, _, min_loc, _ = cv2.minMaxLoc(blurred)
        
        # Simple validation - pupil shouldn't be at edge
        h, w = eye_region.shape[:2]
        x, y = min_loc
        if 0.2 * w < x < 0.8 * w and 0.2 * h < y < 0.8 * h:
            return min_loc
    except Exception as e:
        print(f"[dlib_eye_detector] Pupil detection error: {e}")
    
    return None

def calculate_eye_positions_from_face(face_box, frame_w, frame_h):
    """
    Calculate eye positions using anatomical proportions from face box.
    
    Returns normalized coordinates (0-1):
        - left_eye_box: (x, y, w, h)
        - right_eye_box: (x, y, w, h)
    """
    fx, fy, fw, fh = face_box
    
    # Eye region calculations based on facial proportions
    eye_y = fy + int(fh * 0.30)  # Eyes at 30% from top of face
    eye_h = int(fh * 0.15)       # Eye height is ~15% of face height
    eye_w = int(fw * 0.28)       # Each eye width is ~28% of face width
    
    # Left eye (from viewer's perspective, subject's right)
    left_eye_x = fx + int(fw * 0.56)  # Left eye at 56% from left
    left_eye_box = (
        left_eye_x / frame_w,
        eye_y / frame_h,
        eye_w / frame_w,
        eye_h / frame_h
    )
    
    # Right eye (from viewer's perspective, subject's left)
    right_eye_x = fx + int(fw * 0.16)  # Right eye at 16% from left
    right_eye_box = (
        right_eye_x / frame_w,
        eye_y / frame_h,
        eye_w / frame_w,
        eye_h / frame_h
    )
    
    return left_eye_box, right_eye_box

def extract_eye_data(frame: np.ndarray, frame_w: int, frame_h: int, face_box: Optional[Tuple[int, int, int, int]] = None) -> Dict:
    """
    Extract eye detection data from frame.
    Uses dlib if available, otherwise calculates from face box.
    
    Args:
        frame: BGR image frame
        frame_w: Frame width
        frame_h: Frame height
        face_box: Optional face bounding box (x, y, w, h) from FER
    
    Returns dict with:
        - left_eye_box: (x, y, w, h) normalized 0-1
        - right_eye_box: (x, y, w, h) normalized 0-1  
        - left_pupil: (x, y) normalized 0-1
        - right_pupil: (x, y) normalized 0-1
    """
    # If no face detected, return None values
    if face_box is None:
        return {
            "left_eye_box": None,
            "right_eye_box": None,
            "left_pupil": None,
            "right_pupil": None
        }
    
    # Try dlib if available
    if DLIB_AVAILABLE:
        detector, predictor = _load_dlib_models()
        if detector is not None and predictor is not None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)
            
            if len(faces) > 0:
                face = faces[0]
                landmarks = predictor(gray, face)
                
                # Extract eye landmarks
                left_eye_points = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(36, 42)])
                right_eye_points = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(42, 48)])
                
                # Get eye boxes
                left_eye_rect = cv2.boundingRect(left_eye_points)
                right_eye_rect = cv2.boundingRect(right_eye_points)
                
                lx, ly, lw, lh = left_eye_rect
                rx, ry, rw, rh = right_eye_rect
                
                # Extract eye regions for pupil detection
                left_eye_region = frame[ly:ly+lh, lx:lx+lw]
                right_eye_region = frame[ry:ry+rh, rx:rx+rw]
                
                # Detect pupils
                left_pupil_local = detect_pupil_simple(left_eye_region)
                right_pupil_local = detect_pupil_simple(right_eye_region)
                
                # Convert to normalized coordinates
                left_pupil = None
                if left_pupil_local:
                    left_pupil = ((lx + left_pupil_local[0]) / frame_w, (ly + left_pupil_local[1]) / frame_h)
                
                right_pupil = None
                if right_pupil_local:
                    right_pupil = ((rx + right_pupil_local[0]) / frame_w, (ry + right_pupil_local[1]) / frame_h)
                
                return {
                    "left_eye_box": (lx / frame_w, ly / frame_h, lw / frame_w, lh / frame_h),
                    "right_eye_box": (rx / frame_w, ry / frame_h, rw / frame_w, rh / frame_h),
                    "left_pupil": left_pupil,
                    "right_pupil": right_pupil
                }
    
    # Fallback: Calculate eye positions from face box
    left_eye_box, right_eye_box = calculate_eye_positions_from_face(face_box, frame_w, frame_h)
    
    # Extract eye regions for pupil detection
    lx, ly, lw, lh = (int(left_eye_box[0] * frame_w), int(left_eye_box[1] * frame_h), 
                      int(left_eye_box[2] * frame_w), int(left_eye_box[3] * frame_h))
    rx, ry, rw, rh = (int(right_eye_box[0] * frame_w), int(right_eye_box[1] * frame_h),
                      int(right_eye_box[2] * frame_w), int(right_eye_box[3] * frame_h))
    
    # Ensure regions are within frame bounds
    lx = max(0, min(lx, frame_w - 1))
    ly = max(0, min(ly, frame_h - 1))
    lw = max(1, min(lw, frame_w - lx))
    lh = max(1, min(lh, frame_h - ly))
    
    rx = max(0, min(rx, frame_w - 1))
    ry = max(0, min(ry, frame_h - 1))
    rw = max(1, min(rw, frame_w - rx))
    rh = max(1, min(rh, frame_h - ry))
    
    left_eye_region = frame[ly:ly+lh, lx:lx+lw]
    right_eye_region = frame[ry:ry+rh, rx:rx+rw]
    
    # Detect pupils
    left_pupil_local = detect_pupil_simple(left_eye_region)
    right_pupil_local = detect_pupil_simple(right_eye_region)
    
    # Convert to normalized coordinates
    left_pupil = None
    if left_pupil_local:
        left_pupil = ((lx + left_pupil_local[0]) / frame_w, (ly + left_pupil_local[1]) / frame_h)
    
    right_pupil = None
    if right_pupil_local:
        right_pupil = ((rx + right_pupil_local[0]) / frame_w, (ry + right_pupil_local[1]) / frame_h)
    
    return {
        "left_eye_box": left_eye_box,
        "right_eye_box": right_eye_box,
        "left_pupil": left_pupil,
        "right_pupil": right_pupil
    }
