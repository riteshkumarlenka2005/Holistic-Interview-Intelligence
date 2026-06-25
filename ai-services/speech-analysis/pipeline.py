"""
Speech Analysis Pipeline
Orchestrates the complete speech analysis workflow
"""
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import asyncio

from .whisper_transcriber import (
    WhisperTranscriber,
    TranscriptionResult,
    get_word_timestamps,
    transcribe_file
)
from .prosody_analysis import (
    ProsodyAnalyzer,
    ProsodyResult,
    analyze_prosody
)
from .filler_detection import (
    analyze_fillers,
    FillerAnalysis,
    get_filler_timeline
)
from .confidence_scoring import (
    calculate_confidence_score,
    ConfidenceResult
)


@dataclass
class SpeechAnalysisResult:
    """Complete speech analysis result"""
    transcription: Dict
    prosody: Dict
    fillers: Dict
    confidence: Dict
    timeline: List[Dict]
    summary: Dict


class SpeechAnalysisPipeline:
    """
    Complete speech analysis pipeline combining:
    - ASR transcription with Whisper
    - Prosody analysis with librosa
    - Filler word detection
    - Confidence scoring
    """
    
    def __init__(
        self,
        whisper_model: str = "base",
        device: Optional[str] = None
    ):
        """
        Initialize speech analysis pipeline.
        
        Args:
            whisper_model: Whisper model size (tiny, base, small, medium, large)
            device: Device for inference (cuda, cpu, or None for auto)
        """
        self.transcriber = WhisperTranscriber(
            model_name=whisper_model,
            device=device
        )
        self.prosody_analyzer = ProsodyAnalyzer()
        self.whisper_model = whisper_model
        self.device = device
    
    def analyze(
        self,
        audio_path: str,
        content_quality: Optional[Dict] = None,
        visual_analysis: Optional[Dict] = None,
        include_timeline: bool = True
    ) -> SpeechAnalysisResult:
        """
        Perform complete speech analysis on audio file.
        
        Args:
            audio_path: Path to audio file
            content_quality: Optional content analysis from LLM
            visual_analysis: Optional visual analysis results
            include_timeline: Whether to include timeline data
            
        Returns:
            Complete SpeechAnalysisResult
        """
        # Step 1: Transcribe audio
        transcription = self.transcriber.transcribe(
            audio_path,
            verbatim=True,
            word_timestamps=True
        )
        word_timestamps = get_word_timestamps(transcription)
        
        # Step 2: Analyze prosody
        prosody_result = self.prosody_analyzer.analyze(
            audio_path,
            word_timestamps=word_timestamps
        )
        
        # Convert prosody to dict
        prosody_dict = {
            "pitch": {
                "mean": prosody_result.pitch.mean,
                "std": prosody_result.pitch.std,
                "min": prosody_result.pitch.min,
                "max": prosody_result.pitch.max,
                "range": prosody_result.pitch.range,
                "variability": prosody_result.pitch.variability
            },
            "pace": {
                "words_per_minute": prosody_result.pace.words_per_minute,
                "syllables_per_second": prosody_result.pace.syllables_per_second,
                "assessment": prosody_result.pace.assessment,
                "pauses": prosody_result.pace.pauses,
                "total_pause_duration": prosody_result.pace.total_pause_duration,
                "speech_to_pause_ratio": prosody_result.pace.speech_to_pause_ratio
            },
            "energy": {
                "mean_rms": prosody_result.energy.mean_rms,
                "dynamic_range_db": prosody_result.energy.dynamic_range_db,
                "variation": prosody_result.energy.variation
            },
            "tone": {
                "overall": prosody_result.tone.overall,
                "confidence": prosody_result.tone.confidence_score,
                "monotone_score": prosody_result.tone.monotone_score,
                "expressiveness": prosody_result.tone.expressiveness
            },
            "spectral_features": prosody_result.spectral_features
        }
        
        # Step 3: Detect filler words
        filler_result = analyze_fillers(
            transcription.text,
            word_timestamps,
            transcription.duration
        )
        
        filler_dict = {
            "total_count": filler_result.total_count,
            "filler_rate_per_minute": filler_result.filler_rate_per_minute,
            "category_counts": filler_result.category_counts,
            "most_common": filler_result.most_common,
            "severity": filler_result.severity,
            "recommendations": filler_result.recommendations,
            "instances": [
                {
                    "word": f.word,
                    "start": f.start,
                    "end": f.end,
                    "category": f.category
                }
                for f in filler_result.instances
            ]
        }
        
        # Step 4: Calculate confidence score
        confidence_result = calculate_confidence_score(
            prosody_dict,
            filler_dict,
            content_quality or {},
            visual_analysis
        )
        
        # Step 5: Build timeline if requested
        timeline = []
        if include_timeline:
            timeline = self._build_timeline(
                transcription,
                filler_result,
                prosody_result
            )
        
        # Step 6: Generate summary
        summary = self._generate_summary(
            transcription,
            prosody_dict,
            filler_dict,
            confidence_result
        )
        
        return SpeechAnalysisResult(
            transcription={
                "text": transcription.text,
                "words": word_timestamps,
                "language": transcription.language,
                "duration": transcription.duration
            },
            prosody=prosody_dict,
            fillers=filler_dict,
            confidence=confidence_result,
            timeline=timeline,
            summary=summary
        )
    
    def _build_timeline(
        self,
        transcription: TranscriptionResult,
        fillers: FillerAnalysis,
        prosody: ProsodyResult
    ) -> List[Dict]:
        """Build an event timeline for the speech"""
        events = []
        
        # Add filler word events
        for filler in fillers.instances:
            events.append({
                "time": filler.start,
                "type": "filler",
                "category": filler.category,
                "content": filler.word,
                "severity": "warning" if filler.category == "filler" else "info"
            })
        
        # Add significant pauses
        for pause in prosody.pace.pauses:
            if pause["duration"] >= 0.5:
                events.append({
                    "time": pause["start"],
                    "type": "pause",
                    "category": pause["type"],
                    "duration": pause["duration"],
                    "severity": "warning" if pause["duration"] > 1.5 else "info"
                })
        
        # Sort by time
        events.sort(key=lambda x: x["time"])
        
        return events
    
    def _generate_summary(
        self,
        transcription: TranscriptionResult,
        prosody: Dict,
        fillers: Dict,
        confidence: Dict
    ) -> Dict:
        """Generate overall summary of speech analysis"""
        # Identify strengths
        strengths = []
        if fillers["filler_rate_per_minute"] < 3:
            strengths.append("Minimal use of filler words")
        if prosody["pace"]["assessment"] == "normal":
            strengths.append("Good speaking pace")
        if prosody["tone"]["confidence"] > 0.7:
            strengths.append("Confident vocal delivery")
        if prosody["pitch"]["variability"] == "moderate":
            strengths.append("Engaging vocal variety")
        
        # Identify areas for improvement
        improvements = []
        if fillers["filler_rate_per_minute"] > 5:
            improvements.append("Reduce filler words")
        if prosody["pace"]["assessment"] == "fast":
            improvements.append("Slow down speaking pace")
        elif prosody["pace"]["assessment"] == "slow":
            improvements.append("Increase speaking pace")
        if prosody["tone"]["monotone_score"] > 0.7:
            improvements.append("Add more vocal variety")
        
        return {
            "duration_seconds": transcription.duration,
            "word_count": len(transcription.words),
            "overall_score": confidence["overall_score"],
            "assessment": confidence["assessment"],
            "confidence_level": confidence["confidence_level"],
            "strengths": strengths,
            "areas_for_improvement": improvements,
            "key_metrics": {
                "words_per_minute": prosody["pace"]["words_per_minute"],
                "filler_rate": fillers["filler_rate_per_minute"],
                "voice_confidence": confidence["breakdown"]["voice_confidence"],
                "fluency": confidence["breakdown"]["fluency"]
            }
        }
    
    async def analyze_async(
        self,
        audio_path: str,
        content_quality: Optional[Dict] = None,
        visual_analysis: Optional[Dict] = None
    ) -> SpeechAnalysisResult:
        """Async version of analyze for non-blocking execution"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.analyze(audio_path, content_quality, visual_analysis)
        )


# Convenience functions
async def analyze_speech(
    audio_path: str,
    whisper_model: str = "base",
    content_quality: Optional[Dict] = None
) -> Dict:
    """
    Convenience function to analyze speech from audio file.
    
    Args:
        audio_path: Path to audio file
        whisper_model: Whisper model to use
        content_quality: Optional content analysis
        
    Returns:
        Complete analysis as dictionary
    """
    pipeline = SpeechAnalysisPipeline(whisper_model=whisper_model)
    result = await pipeline.analyze_async(audio_path, content_quality)
    
    return {
        "transcription": result.transcription,
        "prosody": result.prosody,
        "fillers": result.fillers,
        "confidence": result.confidence,
        "timeline": result.timeline,
        "summary": result.summary
    }


def analyze_speech_sync(
    audio_path: str,
    whisper_model: str = "base",
    content_quality: Optional[Dict] = None
) -> Dict:
    """Synchronous version of analyze_speech"""
    pipeline = SpeechAnalysisPipeline(whisper_model=whisper_model)
    result = pipeline.analyze(audio_path, content_quality)
    
    return {
        "transcription": result.transcription,
        "prosody": result.prosody,
        "fillers": result.fillers,
        "confidence": result.confidence,
        "timeline": result.timeline,
        "summary": result.summary
    }
