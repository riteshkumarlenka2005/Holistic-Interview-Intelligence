# Thresholds and Weights for Environment Analysis

# Face Visibility & Tracking
MIN_FACE_VISIBILITY = 0.85
FACE_LOST_TIMEOUT_SEC = 3.0
IDENTITY_MATCH_THRESHOLD = 0.60  # Cosine distance or similar

# Camera & Position
MIN_FPS = 15.0
IDEAL_FACE_SIZE_RATIO = 0.30  # Face should occupy ~30% of screen height
MAX_HORIZONTAL_OFFSET = 0.20  # How far from center is acceptable
MAX_VERTICAL_OFFSET = 0.20

# Audio & Noise
MAX_BACKGROUND_NOISE_RMS = 500  # Placeholder for mic thresholds

# Component Scoring Weights (Total = 100)
WEIGHTS = {
    "camera": 20,
    "microphone": 20,
    "one_person": 20,
    "face_visible": 20,
    "lighting": 10,
    "background": 10
}
