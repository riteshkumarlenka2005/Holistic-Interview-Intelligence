"""
Vision Analysis Pipeline
Orchestrates complete vision analysis combining face, gaze, posture, and expression
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
import numpy as np  # type: ignore[import-untyped]
import time

from .face_landmarks import FaceLandmarkDetector, FaceLandmarks
from .gaze_tracking import GazeTracker, GazeAnalysis
from .posture_detection import PostureDetector, PostureAnalysis
from .micro_expressions import MicroExpressionDetector, ExpressionAnalysis

# Lazy import
cv2: Any = None


def _load_cv2():
    global cv2
    if cv2 is None:
        import cv2 as _cv2  # type: ignore[import-untyped]
        cv2 = _cv2
    return cv2


@dataclass
class FrameAnalysis:
    """Analysis results for a single frame"""
    timestamp: float
    face_detected: bool
    looking_at_camera: bool
    posture_type: str
    dominant_expression: str
    confidence_metrics: Dict


@dataclass
class VisionAnalysisResult:
    """Complete vision analysis result"""
    gaze_analysis: Dict
    posture_analysis: Dict
    expression_analysis: Dict
    timeline: List[Dict]
    summary: Dict


class VisionAnalysisPipeline:
    """
    Complete vision analysis pipeline combining:
    - Face landmark detection
    - Gaze/eye contact tracking
    - Posture detection
    - Micro-expression analysis
    """
    
    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5
    ):
        """
        Initialize vision analysis pipeline.
        
        Args:
            min_detection_confidence: Minimum detection confidence
            min_tracking_confidence: Minimum tracking confidence
        """
        self.face_detector = FaceLandmarkDetector(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.gaze_tracker = GazeTracker(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.posture_detector = PostureDetector(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.expression_detector = MicroExpressionDetector(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        self.frame_analyses: List[FrameAnalysis] = []
        self.start_time: Optional[float] = None
    
    def process_frame(
        self,
        frame: np.ndarray,
        timestamp: Optional[float] = None
    ) -> FrameAnalysis:
        """
        Process a single video frame through all analyzers.
        
        Args:
            frame: BGR image frame
            timestamp: Optional timestamp
            
        Returns:
            FrameAnalysis with results from all modules
        """
        if self.start_time is None:
            self.start_time = time.time()
        
        ts = timestamp if timestamp is not None else time.time() - self.start_time
        
        # Process through each analyzer
        gaze_point = self.gaze_tracker.process_frame(frame, ts)
        posture_point = self.posture_detector.process_frame(frame, ts)
        expression_state = self.expression_detector.process_frame(frame, ts)
        
        # Create frame analysis
        analysis = FrameAnalysis(
            timestamp=ts,
            face_detected=gaze_point.confidence > 0,
            looking_at_camera=gaze_point.looking_at_camera,
            posture_type=posture_point.posture_type,
            dominant_expression=expression_state.dominant_expression,
            confidence_metrics={
                "gaze_confidence": gaze_point.confidence,
                "posture_confidence": posture_point.confidence,
                "expression_confidence": max(expression_state.expression_scores.values()) if expression_state.expression_scores else 0
            }
        )
        
        self.frame_analyses.append(analysis)
        return analysis
    
    def analyze_video(
        self,
        video_path: str,
        sample_rate: int = 3,  # Process every Nth frame
        max_frames: Optional[int] = None
    ) -> VisionAnalysisResult:
        """
        Analyze a video file.
        
        Args:
            video_path: Path to video file
            sample_rate: Process every Nth frame
            max_frames: Maximum frames to process
            
        Returns:
            Complete VisionAnalysisResult
        """
        _load_cv2()
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        frame_count = 0
        processed_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if max_frames and processed_count >= max_frames:
                break
            
            if frame_count % sample_rate == 0:
                timestamp = frame_count / fps
                self.process_frame(frame, timestamp)
                processed_count += 1
            
            frame_count += 1
        
        cap.release()
        
        return self.analyze(duration)
    
    def analyze(self, duration: Optional[float] = None) -> VisionAnalysisResult:
        """
        Analyze all collected data and generate results.
        
        Args:
            duration: Total video duration
            
        Returns:
            Complete VisionAnalysisResult
        """
        # Get analysis from each module
        gaze_result = self.gaze_tracker.analyze(duration)
        posture_result = self.posture_detector.analyze(duration)
        expression_result = self.expression_detector.analyze()
        
        # Build timeline
        timeline = self._build_timeline()
        
        # Generate summary
        summary = self._generate_summary(
            gaze_result, posture_result, expression_result
        )
        
        return VisionAnalysisResult(
            gaze_analysis={
                "eye_contact_percentage": gaze_result.eye_contact_percentage,
                "average_contact_duration": gaze_result.average_contact_duration,
                "gaze_stability": gaze_result.gaze_stability,
                "looking_away_events": gaze_result.looking_away_events,
                "assessment": gaze_result.assessment,
                "recommendations": gaze_result.recommendations
            },
            posture_analysis={
                "dominant_posture": posture_result.dominant_posture,
                "shoulder_alignment": posture_result.average_shoulder_alignment,
                "posture_stability": posture_result.posture_stability,
                "posture_changes": posture_result.posture_changes,
                "hand_movement": {
                    "assessment": posture_result.hand_movement.assessment,
                    "gesture_frequency": posture_result.hand_movement.gesture_frequency
                },
                "engagement_score": posture_result.engagement_score,
                "recommendations": posture_result.recommendations
            },
            expression_analysis={
                "dominant_expression": expression_result.dominant_expression,
                "expression_distribution": expression_result.expression_distribution,
                "micro_expressions_detected": len(expression_result.micro_expressions),
                "authentic_smile_count": expression_result.authentic_smile_count,
                "stress_indicators": expression_result.stress_indicators,
                "emotional_congruence": expression_result.emotional_congruence,
                "assessment": expression_result.assessment,
                "recommendations": expression_result.recommendations
            },
            timeline=timeline,
            summary=summary
        )
    
    def _build_timeline(self) -> List[Dict]:
        """Build event timeline from frame analyses"""
        events = []
        
        # Track significant changes
        prev_looking = None
        looking_away_start = None
        
        for analysis in self.frame_analyses:
            # Eye contact events
            if prev_looking is not None and prev_looking != analysis.looking_at_camera:
                if not analysis.looking_at_camera:
                    looking_away_start = analysis.timestamp
                elif looking_away_start is not None:
                    duration = analysis.timestamp - looking_away_start
                    if duration > 1.0:  # Only log significant breaks
                        events.append({
                            "time": looking_away_start,
                            "type": "gaze_break",
                            "duration": duration,
                            "severity": "warning" if duration > 3 else "info"
                        })
                    looking_away_start = None
            
            prev_looking = analysis.looking_at_camera
        
        # Add micro-expression events
        for me in self.expression_detector.micro_expressions:
            events.append({
                "time": me.timestamp,
                "type": "micro_expression",
                "expression": me.expression,
                "intensity": me.intensity,
                "severity": "info" if me.expression in ["happy", "surprised"] else "warning"
            })
        
        events.sort(key=lambda x: x["time"])
        return events
    
    def _generate_summary(
        self,
        gaze: GazeAnalysis,
        posture: PostureAnalysis,
        expression: ExpressionAnalysis
    ) -> Dict:
        """Generate overall summary"""
        strengths = []
        improvements = []
        
        # Gaze
        if gaze.eye_contact_percentage >= 60:
            strengths.append("Good eye contact maintained")
        elif gaze.eye_contact_percentage < 40:
            improvements.append("Improve eye contact")
        
        # Posture
        if posture.dominant_posture == "upright" and posture.posture_stability > 0.6:
            strengths.append("Professional posture")
        elif posture.dominant_posture in ["slouching", "leaning_left", "leaning_right"]:
            improvements.append("Work on posture")
        
        # Expression
        if expression.authentic_smile_count > 2:
            strengths.append("Positive facial expressions")
        if expression.stress_indicators > 3:
            improvements.append("Manage visible stress signs")
        
        # Calculate overall score
        scores = [
            gaze.eye_contact_percentage / 100,
            posture.engagement_score,
            expression.emotional_congruence * 0.8 + 0.2
        ]
        overall_score = np.mean(scores)
        
        return {
            "overall_visual_score": float(overall_score),
            "eye_contact_score": gaze.eye_contact_percentage,
            "posture_score": posture.engagement_score * 100,
            "expression_score": expression.emotional_congruence * 100,
            "strengths": strengths,
            "areas_for_improvement": improvements,
            "total_frames_analyzed": len(self.frame_analyses)
        }
    
    def reset(self):
        """Reset all analyzers"""
        self.gaze_tracker.reset()
        self.posture_detector.reset()
        self.expression_detector.reset()
        self.frame_analyses = []
        self.start_time = None
    
    def close(self):
        """Release all resources"""
        self.face_detector.close()
        self.gaze_tracker.close()
        self.posture_detector.close()
        self.expression_detector.close()


# Convenience functions
def analyze_video(video_path: str, sample_rate: int = 3) -> Dict:
    """
    Analyze a video file for visual communication cues.
    
    Args:
        video_path: Path to video file
        sample_rate: Process every Nth frame
        
    Returns:
        Complete analysis as dictionary
    """
    pipeline = VisionAnalysisPipeline()
    try:
        result = pipeline.analyze_video(video_path, sample_rate)
        return {
            "gaze": result.gaze_analysis,
            "posture": result.posture_analysis,
            "expression": result.expression_analysis,
            "timeline": result.timeline,
            "summary": result.summary
        }
    finally:
        pipeline.close()


def analyze_frame(frame: np.ndarray) -> Dict:
    """
    Analyze a single frame.
    
    Args:
        frame: BGR image frame
        
    Returns:
        Frame analysis as dictionary
    """
    pipeline = VisionAnalysisPipeline()
    try:
        analysis = pipeline.process_frame(frame)
        return {
            "face_detected": analysis.face_detected,
            "looking_at_camera": analysis.looking_at_camera,
            "posture_type": analysis.posture_type,
            "dominant_expression": analysis.dominant_expression,
            "confidence": analysis.confidence_metrics
        }
    finally:
        pipeline.close()
