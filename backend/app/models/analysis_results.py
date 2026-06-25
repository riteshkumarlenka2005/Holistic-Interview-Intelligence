from sqlalchemy import Column, String, Text, Float, Integer, ForeignKey, Index, JSON, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class SpeechMetrics(BaseModel):
    __tablename__ = "speech_metrics"
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    response_id = Column(String(36), ForeignKey("responses.id", ondelete="CASCADE"), nullable=True)
    words_per_minute = Column(Float, nullable=True)
    total_words = Column(Integer, nullable=True)
    total_duration_seconds = Column(Float, nullable=True)
    pause_count = Column(Integer, nullable=True)
    avg_pause_duration_ms = Column(Float, nullable=True)
    filler_count = Column(Integer, nullable=True)
    filler_words = Column(JSON, default=list)
    filler_rate_per_minute = Column(Float, nullable=True)
    fluency_score = Column(Float, nullable=True)
    clarity_score = Column(Float, nullable=True)
    pronunciation_score = Column(Float, nullable=True)
    grammar_score = Column(Float, nullable=True)
    vocabulary_richness = Column(Float, nullable=True)
    grammar_issues = Column(JSON, default=list)
    prosody = Column(JSON, default=dict)

class FaceMetrics(BaseModel):
    __tablename__ = "face_metrics"
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    face_visibility_pct = Column(Float, nullable=True)
    avg_confidence_score = Column(Float, nullable=True)
    smile_index = Column(Float, nullable=True)
    engagement_score = Column(Float, nullable=True)
    dominant_expression = Column(String(30), nullable=True)
    expression_timeline = Column(JSON, default=list)
    head_pose_summary = Column(JSON, default=dict)
    blink_rate_per_minute = Column(Float, nullable=True)
    frame_count = Column(Integer, nullable=True)

class EyeTrackingData(BaseModel):
    __tablename__ = "eye_tracking_data"
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    eye_contact_pct = Column(Float, nullable=True)
    avg_contact_duration_ms = Column(Float, nullable=True)
    gaze_stability_score = Column(Float, nullable=True)
    gaze_distribution = Column(JSON, default=dict)
    gaze_off_events = Column(JSON, default=list)
    fixation_count = Column(Integer, nullable=True)
    distraction_count = Column(Integer, nullable=True)

class EmotionTimeline(BaseModel):
    __tablename__ = "emotion_timeline"
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp_ms = Column(Integer, nullable=False, index=True)
    text_emotion = Column(String(20), nullable=True)
    face_emotion = Column(String(20), nullable=True)
    fused_emotion = Column(String(20), nullable=True)
    text_emotion_scores = Column(JSON, default=dict)
    face_emotion_scores = Column(JSON, default=dict)
    intensity = Column(Float, nullable=True)
    is_congruent = Column(Boolean, nullable=True)

class ConfidenceTimeline(BaseModel):
    __tablename__ = "confidence_timeline"
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp_ms = Column(Integer, nullable=False, index=True)
    vocal_confidence = Column(Float, nullable=True)
    visual_confidence = Column(Float, nullable=True)
    fused_confidence = Column(Float, nullable=True)
    breakdown = Column(JSON, default=dict)

class TechnicalScore(BaseModel):
    __tablename__ = "technical_scores"
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    response_id = Column(String(36), ForeignKey("responses.id", ondelete="CASCADE"), nullable=True)
    question_id = Column(String(36), ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=True)
    accuracy_score = Column(Float, nullable=True)
    depth_score = Column(Float, nullable=True)
    completeness_score = Column(Float, nullable=True)
    examples_score = Column(Float, nullable=True)
    industry_language_score = Column(Float, nullable=True)
    overall_technical_score = Column(Float, nullable=True)
    llm_feedback = Column(Text, nullable=True)
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    missing_concepts = Column(JSON, default=list)
    llm_model_used = Column(String(50), nullable=True)

class CommunicationScore(BaseModel):
    __tablename__ = "communication_scores"
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    grammar_score = Column(Float, nullable=True)
    vocabulary_score = Column(Float, nullable=True)
    clarity_score = Column(Float, nullable=True)
    fluency_score = Column(Float, nullable=True)
    discourse_score = Column(Float, nullable=True)
    structure_score = Column(Float, nullable=True)
    star_method_used = Column(Boolean, nullable=True)
    overall_communication_score = Column(Float, nullable=True)
    improvement_suggestions = Column(JSON, default=list)
