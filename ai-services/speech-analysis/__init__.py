"""
Speech Analysis Module
Complete speech analysis including transcription, prosody, fillers, and confidence scoring
"""

from .whisper_transcriber import (
    WhisperTranscriber,
    TranscriptionResult,
    TranscriptionWord,
    get_word_timestamps,
    transcribe_file,
    get_transcriber
)

from .prosody_analysis import (
    ProsodyAnalyzer,
    ProsodyResult,
    PitchAnalysis,
    PaceAnalysis,
    EnergyAnalysis,
    ToneAnalysis,
    analyze_prosody,
    calculate_speaking_pace
)

from .filler_detection import (
    FillerInstance,
    FillerAnalysis,
    detect_fillers,
    analyze_fillers,
    calculate_filler_rate,
    get_filler_timeline,
    FILLER_CATEGORIES
)

from .confidence_scoring import (
    ConfidenceBreakdown,
    ConfidenceResult,
    calculate_confidence_score,
    get_assessment_label
)

from .pipeline import (
    SpeechAnalysisPipeline,
    SpeechAnalysisResult,
    analyze_speech,
    analyze_speech_sync
)

__all__ = [
    # Transcription
    "WhisperTranscriber",
    "TranscriptionResult",
    "TranscriptionWord",
    "get_word_timestamps",
    "transcribe_file",
    "get_transcriber",
    
    # Prosody
    "ProsodyAnalyzer",
    "ProsodyResult",
    "PitchAnalysis",
    "PaceAnalysis",
    "EnergyAnalysis",
    "ToneAnalysis",
    "analyze_prosody",
    "calculate_speaking_pace",
    
    # Fillers
    "FillerInstance",
    "FillerAnalysis",
    "detect_fillers",
    "analyze_fillers",
    "calculate_filler_rate",
    "get_filler_timeline",
    "FILLER_CATEGORIES",
    
    # Confidence
    "ConfidenceBreakdown",
    "ConfidenceResult",
    "calculate_confidence_score",
    "get_assessment_label",
    
    # Pipeline
    "SpeechAnalysisPipeline",
    "SpeechAnalysisResult",
    "analyze_speech",
    "analyze_speech_sync"
]
