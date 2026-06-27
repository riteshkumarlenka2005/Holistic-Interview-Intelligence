"""
Emotion Engine — CPU-Optimized Facial Expression Analysis.

Uses DeepFace (VGG-Face emotion backbone) to classify emotions.
Bypasses face detection completely by taking a pre-cropped face bounding box.
Implements probability smoothing and state tracking via EmotionState.
"""
import time
import numpy as np
import cv2
from typing import Dict, Any, Optional
from app.models.emotion_state import EmotionState

# Lazy load DeepFace to avoid blocking imports
DeepFace = None

def _load_deepface():
    global DeepFace
    if DeepFace is None:
        try:
            from deepface import DeepFace as _DeepFace
            DeepFace = _DeepFace
            print("[EmotionEngine] DeepFace loaded successfully.")
        except ImportError:
            print("[EmotionEngine] Warning: DeepFace not installed.")
            DeepFace = None


class EmotionEngine:
    def __init__(self):
        _load_deepface()
        # Track state per session: session_id -> EmotionState
        self.session_states: Dict[str, EmotionState] = {}
        
        # Configuration
        self.min_interval_seconds = 3.0  # Only analyze every 3 seconds
        self.history_size = 5            # Number of probability vectors to average
        self.confidence_threshold = 40.0 # Drop predictions below 40% confidence

    def get_state(self, session_id: str) -> EmotionState:
        """Retrieve or initialize state for a session."""
        if session_id not in self.session_states:
            self.session_states[session_id] = EmotionState()
        return self.session_states[session_id]

    def preprocess(self, face_crop: np.ndarray) -> Optional[np.ndarray]:
        """
        Preprocess the raw face crop from MediaPipe.
        Resizes to 224x224 and ensures it's a valid BGR array for DeepFace.
        """
        if face_crop is None or face_crop.size == 0:
            return None
            
        try:
            # Resize to DeepFace's default expected input size to avoid internal resizing overhead
            resized = cv2.resize(face_crop, (224, 224))
            return resized
        except Exception as e:
            print(f"[EmotionEngine] Error preprocessing face crop: {e}")
            return None

    def analyze_emotion(self, session_id: str, face_crop: np.ndarray, timestamp_ms: int) -> EmotionState:
        """
        Main entry point for emotion analysis.
        Implements in-memory throttling, smoothing, and timeline tracking.
        """
        state = self.get_state(session_id)
        current_time = time.time()

        # 1. In-Memory Throttling: Skip if min interval hasn't passed
        if (current_time - state.last_analysis_time) < self.min_interval_seconds:
            return state

        # We are going to analyze. Update the timestamp immediately.
        state.last_analysis_time = current_time

        if DeepFace is None:
            return state

        # 2. Preprocess the raw crop
        processed_crop = self.preprocess(face_crop)
        if processed_crop is None:
            return state

        # 3. Inference via DeepFace (Bypassing Detector)
        try:
            # DeepFace returns a list of dicts when analyzing images.
            # Using enforce_detection=False prevents crashes if the crop doesn't clearly show a full face.
            # detector_backend="skip" bypasses MTCNN/RetinaFace overhead.
            results = DeepFace.analyze(
                img_path=processed_crop,
                actions=["emotion"],
                enforce_detection=False,
                detector_backend="skip",
                silent=True
            )
            
            # DeepFace might return a list or dict depending on version. Handle both.
            result = results[0] if isinstance(results, list) else results
            emotion_probabilities = result.get("emotion", {})
            
            if not emotion_probabilities:
                return state

            # 4. Probability Averaging (Smoothing)
            state.emotion_history.append(emotion_probabilities)
            if len(state.emotion_history) > self.history_size:
                state.emotion_history.pop(0)

            # Average the probabilities across the rolling buffer
            avg_probs = {}
            for e_dict in state.emotion_history:
                for emotion, prob in e_dict.items():
                    avg_probs[emotion] = avg_probs.get(emotion, 0.0) + prob
                    
            for emotion in avg_probs:
                avg_probs[emotion] /= len(state.emotion_history)

            # Find the emotion with the highest average probability
            best_emotion = max(avg_probs.items(), key=lambda x: x[1])
            emotion_name = best_emotion[0]
            confidence = best_emotion[1]

            # 5. Confidence Thresholding
            if confidence >= self.confidence_threshold:
                state.current_emotion = emotion_name
                state.confidence = confidence
                # Map confidence to a 0.0-1.0 score for generic metric usage if needed
                state.emotion_score = confidence / 100.0
            else:
                # If too low, default to neutral
                state.current_emotion = "neutral"
                state.confidence = confidence

            # 6. Update Timeline
            # Append triplet: (timestamp_ms, emotion, confidence)
            state.timeline.append((timestamp_ms, state.current_emotion, state.confidence))

        except Exception as e:
            print(f"[EmotionEngine] DeepFace analysis error: {e}")

        return state
