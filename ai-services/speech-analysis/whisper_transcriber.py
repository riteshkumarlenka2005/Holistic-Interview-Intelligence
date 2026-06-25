"""
Whisper ASR Transcription Module
Provides verbatim transcription with word-level timestamps
"""
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np

# Lazy imports for optional dependencies
whisper = None
torch = None


def _load_whisper():
    """Lazy load whisper to avoid import errors if not installed"""
    global whisper, torch
    if whisper is None:
        try:
            import whisper as _whisper
            import torch as _torch
            whisper = _whisper
            torch = _torch
        except ImportError:
            raise ImportError(
                "Whisper is not installed. Install with: pip install openai-whisper"
            )
    return whisper


@dataclass
class TranscriptionWord:
    """Represents a single transcribed word with timing"""
    word: str
    start: float
    end: float
    confidence: float


@dataclass
class TranscriptionResult:
    """Complete transcription result"""
    text: str
    words: List[TranscriptionWord]
    language: str
    duration: float
    segments: List[Dict]


class WhisperTranscriber:
    """
    Whisper-based transcription with verbatim mode for interview analysis.
    Preserves filler words and hesitations for accurate analysis.
    """
    
    SUPPORTED_MODELS = ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]
    
    def __init__(
        self,
        model_name: str = "base",
        device: Optional[str] = None,
        compute_type: str = "float16"
    ):
        """
        Initialize Whisper transcriber.
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large, large-v3)
            device: Device to use (cuda, cpu, or None for auto-detect)
            compute_type: Computation type (float16, float32, int8)
        """
        _load_whisper()
        
        if model_name not in self.SUPPORTED_MODELS:
            raise ValueError(f"Model must be one of: {self.SUPPORTED_MODELS}")
        
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.compute_type = compute_type
        self.model = None
    
    def load_model(self) -> None:
        """Load the Whisper model into memory"""
        if self.model is None:
            self.model = whisper.load_model(self.model_name, device=self.device)
    
    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe",
        verbatim: bool = True,
        word_timestamps: bool = True
    ) -> TranscriptionResult:
        """
        Transcribe audio file with word-level timestamps.
        
        Args:
            audio_path: Path to audio file
            language: Language code (e.g., 'en', 'es') or None for auto-detect
            task: 'transcribe' or 'translate'
            verbatim: If True, preserve filler words and hesitations
            word_timestamps: If True, include word-level timestamps
            
        Returns:
            TranscriptionResult with full transcription and word timings
        """
        self.load_model()
        
        # Whisper options for verbatim transcription
        options = {
            "language": language,
            "task": task,
            "word_timestamps": word_timestamps,
            "verbose": False,
        }
        
        # For verbatim mode, we don't suppress tokens
        if verbatim:
            options["suppress_tokens"] = []  # Don't suppress anything
            options["condition_on_previous_text"] = True
        
        result = self.model.transcribe(audio_path, **options)
        
        # Extract word-level information
        words = []
        if word_timestamps and "segments" in result:
            for segment in result["segments"]:
                if "words" in segment:
                    for word_info in segment["words"]:
                        words.append(TranscriptionWord(
                            word=word_info.get("word", "").strip(),
                            start=word_info.get("start", 0.0),
                            end=word_info.get("end", 0.0),
                            confidence=word_info.get("probability", 1.0)
                        ))
        
        # Calculate duration from segments
        duration = 0.0
        if result.get("segments"):
            duration = result["segments"][-1].get("end", 0.0)
        
        return TranscriptionResult(
            text=result.get("text", "").strip(),
            words=words,
            language=result.get("language", "en"),
            duration=duration,
            segments=result.get("segments", [])
        )
    
    def transcribe_audio_array(
        self,
        audio_array: np.ndarray,
        sample_rate: int = 16000,
        **kwargs
    ) -> TranscriptionResult:
        """
        Transcribe from numpy audio array.
        
        Args:
            audio_array: Audio data as numpy array
            sample_rate: Sample rate of audio (Whisper expects 16kHz)
            **kwargs: Additional arguments passed to transcribe()
            
        Returns:
            TranscriptionResult
        """
        self.load_model()
        
        # Resample if needed
        if sample_rate != 16000:
            try:
                import librosa
                audio_array = librosa.resample(
                    audio_array.astype(np.float32),
                    orig_sr=sample_rate,
                    target_sr=16000
                )
            except ImportError:
                raise ImportError("librosa required for resampling")
        
        # Normalize audio
        if audio_array.dtype != np.float32:
            audio_array = audio_array.astype(np.float32)
        if audio_array.max() > 1.0:
            audio_array = audio_array / 32768.0
        
        # Transcribe
        options = {
            "word_timestamps": True,
            "verbose": False,
            **kwargs
        }
        
        result = self.model.transcribe(audio_array, **options)
        
        words = []
        if "segments" in result:
            for segment in result["segments"]:
                if "words" in segment:
                    for word_info in segment["words"]:
                        words.append(TranscriptionWord(
                            word=word_info.get("word", "").strip(),
                            start=word_info.get("start", 0.0),
                            end=word_info.get("end", 0.0),
                            confidence=word_info.get("probability", 1.0)
                        ))
        
        duration = result["segments"][-1]["end"] if result.get("segments") else 0.0
        
        return TranscriptionResult(
            text=result.get("text", "").strip(),
            words=words,
            language=result.get("language", "en"),
            duration=duration,
            segments=result.get("segments", [])
        )


def get_word_timestamps(result: TranscriptionResult) -> List[Dict]:
    """
    Convert TranscriptionResult words to list of dicts for compatibility.
    
    Args:
        result: TranscriptionResult object
        
    Returns:
        List of word dictionaries with start, end, word, confidence
    """
    return [
        {
            "word": w.word,
            "start": w.start,
            "end": w.end,
            "confidence": w.confidence
        }
        for w in result.words
    ]


# Singleton instance for convenience
_default_transcriber: Optional[WhisperTranscriber] = None


def get_transcriber(model_name: str = "base") -> WhisperTranscriber:
    """Get or create a default transcriber instance"""
    global _default_transcriber
    if _default_transcriber is None or _default_transcriber.model_name != model_name:
        _default_transcriber = WhisperTranscriber(model_name=model_name)
    return _default_transcriber


async def transcribe_file(
    audio_path: str,
    model_name: str = "base",
    verbatim: bool = True
) -> Dict:
    """
    Async-friendly transcription function.
    
    Args:
        audio_path: Path to audio file
        model_name: Whisper model to use
        verbatim: Preserve filler words
        
    Returns:
        Dictionary with transcription results
    """
    import asyncio
    
    def _transcribe():
        transcriber = get_transcriber(model_name)
        result = transcriber.transcribe(audio_path, verbatim=verbatim)
        return {
            "text": result.text,
            "words": get_word_timestamps(result),
            "language": result.language,
            "duration": result.duration,
            "segments": result.segments
        }
    
    # Run in executor to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _transcribe)
