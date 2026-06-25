"""
Multimodal Reasoning Module
Complete multimodal analysis for interview assessment
"""

from .fusion import (
    MultimodalFusion,
    FusionResult,
    FusionWeights,
    CongruenceResult,
    fuse_modalities,
    detect_incongruence
)

from .timeline_builder import (
    TimelineBuilder,
    TimelineEvent,
    MultimodalTranscript,
    MultimodalSegment,
    EventType,
    EventSeverity,
    build_timeline,
    build_multimodal_transcript
)

from .llm_reasoner import (
    LLMReasoner,
    LLMConfig,
    FeedbackResult,
    analyze_with_llm,
    generate_feedback
)

from .pipeline import (
    MultimodalReasoningPipeline,
    ReasoningResult,
    analyze_interview
)

__all__ = [
    # Fusion
    "MultimodalFusion",
    "FusionResult",
    "FusionWeights",
    "CongruenceResult",
    "fuse_modalities",
    "detect_incongruence",
    
    # Timeline
    "TimelineBuilder",
    "TimelineEvent",
    "MultimodalTranscript",
    "MultimodalSegment",
    "EventType",
    "EventSeverity",
    "build_timeline",
    "build_multimodal_transcript",
    
    # LLM Reasoner
    "LLMReasoner",
    "LLMConfig",
    "FeedbackResult",
    "analyze_with_llm",
    "generate_feedback",
    
    # Pipeline
    "MultimodalReasoningPipeline",
    "ReasoningResult",
    "analyze_interview"
]
