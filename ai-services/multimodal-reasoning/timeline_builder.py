"""
Timeline Builder Module
Creates multimodal transcripts and event timelines for interview analysis
"""
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json


class EventType(Enum):
    """Types of behavioral events"""
    SPEECH = "speech"
    FILLER = "filler"
    PAUSE = "pause"
    GAZE_BREAK = "gaze_break"
    POSTURE_CHANGE = "posture_change"
    MICRO_EXPRESSION = "micro_expression"
    STRESS_INDICATOR = "stress_indicator"
    HIGHLIGHT = "highlight"  # Positive events


class EventSeverity(Enum):
    """Severity levels for events"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    POSITIVE = "positive"


@dataclass
class TimelineEvent:
    """A single event in the timeline"""
    timestamp: float
    end_time: Optional[float]
    event_type: EventType
    category: str
    content: str
    severity: EventSeverity
    metadata: Dict


@dataclass
class MultimodalSegment:
    """A segment of the multimodal transcript"""
    start_time: float
    end_time: float
    text: str
    gaze_status: str  # looking_at_camera, looking_away, etc.
    posture: str
    expression: str
    tone: str
    events: List[TimelineEvent]
    annotations: List[str]


@dataclass
class MultimodalTranscript:
    """Complete multimodal transcript with behavioral annotations"""
    segments: List[MultimodalSegment]
    events: List[TimelineEvent]
    summary: Dict
    formatted_text: str


class TimelineBuilder:
    """
    Builds multimodal transcripts and event timelines.
    Combines speech transcription with behavioral annotations.
    """
    
    def __init__(self):
        self.events: List[TimelineEvent] = []
        self.segments: List[MultimodalSegment] = []
    
    def add_speech_events(
        self,
        transcription: Dict,
        prosody: Dict,
        fillers: Dict
    ) -> None:
        """
        Add speech-related events to timeline.
        
        Args:
            transcription: Transcription with word timestamps
            prosody: Prosody analysis results
            fillers: Filler word analysis results
        """
        # Add filler word events
        filler_instances = fillers.get("instances", [])
        for filler in filler_instances:
            self.events.append(TimelineEvent(
                timestamp=filler.get("start", 0),
                end_time=filler.get("end"),
                event_type=EventType.FILLER,
                category=filler.get("category", "filler"),
                content=filler.get("word", ""),
                severity=EventSeverity.WARNING,
                metadata={"confidence": filler.get("confidence", 1.0)}
            ))
        
        # Add pause events
        pauses = prosody.get("pace", {}).get("pauses", [])
        for pause in pauses:
            if pause.get("duration", 0) > 0.5:
                severity = EventSeverity.WARNING if pause.get("duration", 0) > 2.0 else EventSeverity.INFO
                self.events.append(TimelineEvent(
                    timestamp=pause.get("start", 0),
                    end_time=pause.get("end"),
                    event_type=EventType.PAUSE,
                    category=pause.get("type", "pause"),
                    content=f"{pause.get('duration', 0):.1f}s pause",
                    severity=severity,
                    metadata={"duration": pause.get("duration", 0)}
                ))
    
    def add_vision_events(
        self,
        gaze_analysis: Dict,
        posture_analysis: Dict,
        expression_analysis: Dict
    ) -> None:
        """
        Add vision-related events to timeline.
        
        Args:
            gaze_analysis: Gaze tracking results
            posture_analysis: Posture detection results
            expression_analysis: Expression analysis results
        """
        # Add gaze break events
        looking_away = gaze_analysis.get("looking_away_events", [])
        for event in looking_away:
            severity = EventSeverity.WARNING if event.get("duration", 0) > 3 else EventSeverity.INFO
            self.events.append(TimelineEvent(
                timestamp=event.get("start", 0),
                end_time=event.get("end"),
                event_type=EventType.GAZE_BREAK,
                category=event.get("direction", "away"),
                content=f"Looked {event.get('direction', 'away')} for {event.get('duration', 0):.1f}s",
                severity=severity,
                metadata={"direction": event.get("direction"), "duration": event.get("duration")}
            ))
        
        # Add micro-expression events (if available in detailed form)
        # These would come from the expression analysis micro_expressions list
        micro_expr_count = expression_analysis.get("micro_expressions_detected", 0)
        if micro_expr_count > 0:
            # Add summary event
            self.events.append(TimelineEvent(
                timestamp=0,
                end_time=None,
                event_type=EventType.MICRO_EXPRESSION,
                category="summary",
                content=f"{micro_expr_count} micro-expressions detected",
                severity=EventSeverity.INFO,
                metadata={"count": micro_expr_count}
            ))
        
        # Add stress indicator summary if present
        stress_count = expression_analysis.get("stress_indicators", 0)
        if stress_count > 3:
            self.events.append(TimelineEvent(
                timestamp=0,
                end_time=None,
                event_type=EventType.STRESS_INDICATOR,
                category="facial",
                content=f"{stress_count} stress indicators detected",
                severity=EventSeverity.WARNING,
                metadata={"count": stress_count}
            ))
    
    def add_highlight(
        self,
        timestamp: float,
        content: str,
        category: str = "positive"
    ) -> None:
        """
        Add a positive highlight event.
        
        Args:
            timestamp: Event time
            content: Description of highlight
            category: Highlight category
        """
        self.events.append(TimelineEvent(
            timestamp=timestamp,
            end_time=None,
            event_type=EventType.HIGHLIGHT,
            category=category,
            content=content,
            severity=EventSeverity.POSITIVE,
            metadata={}
        ))
    
    def build_multimodal_transcript(
        self,
        transcription: Dict,
        vision_timeline: List[Dict],
        speech_timeline: List[Dict],
        segment_duration: float = 10.0
    ) -> MultimodalTranscript:
        """
        Build a complete multimodal transcript with annotations.
        
        Args:
            transcription: Speech transcription with word timestamps
            vision_timeline: Timeline of visual events
            speech_timeline: Timeline of speech events  
            segment_duration: Duration of each segment in seconds
            
        Returns:
            Complete MultimodalTranscript
        """
        words = transcription.get("words", [])
        total_duration = transcription.get("duration", 0)
        
        if not words:
            return MultimodalTranscript(
                segments=[],
                events=self.events,
                summary={"total_duration": total_duration},
                formatted_text=""
            )
        
        # Create segments
        segments = []
        current_time = 0
        
        while current_time < total_duration:
            segment_end = min(current_time + segment_duration, total_duration)
            
            # Get words in this segment
            segment_words = [
                w for w in words
                if current_time <= w.get("start", 0) < segment_end
            ]
            
            # Get text for segment
            segment_text = " ".join(w.get("word", "") for w in segment_words)
            
            # Get events in this segment
            segment_events = [
                e for e in self.events
                if current_time <= e.timestamp < segment_end
            ]
            
            # Determine visual state (simplified - use mode)
            gaze_status = "looking_at_camera"  # Default
            posture = "upright"  # Default
            expression = "neutral"  # Default
            tone = "neutral"  # Default
            
            # Generate annotations
            annotations = []
            for event in segment_events:
                if event.event_type == EventType.FILLER:
                    annotations.append(f"[Filler: {event.content}]")
                elif event.event_type == EventType.GAZE_BREAK:
                    annotations.append(f"[Gaze: {event.content}]")
                elif event.event_type == EventType.PAUSE:
                    annotations.append(f"[Pause: {event.metadata.get('duration', 0):.1f}s]")
            
            if segment_text.strip():
                segments.append(MultimodalSegment(
                    start_time=current_time,
                    end_time=segment_end,
                    text=segment_text.strip(),
                    gaze_status=gaze_status,
                    posture=posture,
                    expression=expression,
                    tone=tone,
                    events=segment_events,
                    annotations=annotations
                ))
            
            current_time = segment_end
        
        # Generate formatted text
        formatted_text = self._format_transcript(segments)
        
        # Generate summary
        summary = self._generate_summary(segments)
        
        return MultimodalTranscript(
            segments=segments,
            events=sorted(self.events, key=lambda e: e.timestamp),
            summary=summary,
            formatted_text=formatted_text
        )
    
    def _format_transcript(self, segments: List[MultimodalSegment]) -> str:
        """Format transcript with inline annotations"""
        lines = []
        
        for segment in segments:
            timestamp = f"[{self._format_time(segment.start_time)}]"
            
            # Build annotated text
            text = segment.text
            if segment.annotations:
                annotations_str = " ".join(segment.annotations)
                text = f"{text} {annotations_str}"
            
            # Add visual context
            context_parts = []
            if segment.gaze_status != "looking_at_camera":
                context_parts.append(f"Gaze: {segment.gaze_status}")
            if segment.expression != "neutral":
                context_parts.append(f"Expression: {segment.expression}")
            if segment.tone != "neutral":
                context_parts.append(f"Tone: {segment.tone}")
            
            context = f" ({'; '.join(context_parts)})" if context_parts else ""
            
            lines.append(f"{timestamp} Candidate: {text}{context}")
        
        return "\n".join(lines)
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
    
    def _generate_summary(self, segments: List[MultimodalSegment]) -> Dict:
        """Generate timeline summary statistics"""
        total_events = len(self.events)
        
        event_counts = {}
        for event in self.events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        warning_events = [e for e in self.events if e.severity == EventSeverity.WARNING]
        positive_events = [e for e in self.events if e.severity == EventSeverity.POSITIVE]
        
        return {
            "total_segments": len(segments),
            "total_events": total_events,
            "event_counts": event_counts,
            "warning_count": len(warning_events),
            "positive_count": len(positive_events),
            "events_by_type": event_counts
        }
    
    def get_events_in_range(
        self,
        start_time: float,
        end_time: float
    ) -> List[TimelineEvent]:
        """Get events within a time range"""
        return [
            e for e in self.events
            if start_time <= e.timestamp <= end_time
        ]
    
    def get_events_by_type(self, event_type: EventType) -> List[TimelineEvent]:
        """Get all events of a specific type"""
        return [e for e in self.events if e.event_type == event_type]
    
    def to_dict(self) -> Dict:
        """Convert timeline to dictionary format"""
        return {
            "events": [
                {
                    "timestamp": e.timestamp,
                    "end_time": e.end_time,
                    "type": e.event_type.value,
                    "category": e.category,
                    "content": e.content,
                    "severity": e.severity.value,
                    "metadata": e.metadata
                }
                for e in sorted(self.events, key=lambda x: x.timestamp)
            ]
        }
    
    def reset(self):
        """Reset timeline"""
        self.events = []
        self.segments = []


def build_timeline(
    speech_analysis: Dict,
    vision_analysis: Dict
) -> Dict:
    """
    Build a timeline from speech and vision analysis.
    
    Args:
        speech_analysis: Complete speech analysis results
        vision_analysis: Complete vision analysis results
        
    Returns:
        Timeline as dictionary
    """
    builder = TimelineBuilder()
    
    # Add speech events
    builder.add_speech_events(
        speech_analysis.get("transcription", {}),
        speech_analysis.get("prosody", {}),
        speech_analysis.get("fillers", {})
    )
    
    # Add vision events
    builder.add_vision_events(
        vision_analysis.get("gaze_analysis", {}),
        vision_analysis.get("posture_analysis", {}),
        vision_analysis.get("expression_analysis", {})
    )
    
    return builder.to_dict()


def build_multimodal_transcript(
    speech_analysis: Dict,
    vision_analysis: Dict
) -> Dict:
    """
    Build a multimodal transcript with annotations.
    
    Args:
        speech_analysis: Complete speech analysis results
        vision_analysis: Complete vision analysis results
        
    Returns:
        Multimodal transcript as dictionary
    """
    builder = TimelineBuilder()
    
    # Add all events
    builder.add_speech_events(
        speech_analysis.get("transcription", {}),
        speech_analysis.get("prosody", {}),
        speech_analysis.get("fillers", {})
    )
    builder.add_vision_events(
        vision_analysis.get("gaze_analysis", {}),
        vision_analysis.get("posture_analysis", {}),
        vision_analysis.get("expression_analysis", {})
    )
    
    # Build transcript
    transcript = builder.build_multimodal_transcript(
        speech_analysis.get("transcription", {}),
        vision_analysis.get("timeline", []),
        speech_analysis.get("timeline", [])
    )
    
    return {
        "segments": [
            {
                "start": s.start_time,
                "end": s.end_time,
                "text": s.text,
                "gaze": s.gaze_status,
                "posture": s.posture,
                "expression": s.expression,
                "annotations": s.annotations
            }
            for s in transcript.segments
        ],
        "formatted_text": transcript.formatted_text,
        "summary": transcript.summary,
        "events": builder.to_dict()["events"]
    }
