"""
Speech Analysis Service
Real-time speech analysis including transcription, grammar checking, and emotion detection.
Integrates faster-whisper, LanguageTool, and HuggingFace emotion models.
"""
import base64
import tempfile
import os
import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from collections import deque
import numpy as np

# Lazy-loaded dependencies
whisper_model = None
emotion_classifier = None

# LanguageTool server configuration
LT_LOCAL_SERVER = "http://localhost:8081"
LT_PUBLIC_API = "https://api.languagetoolplus.com/v2/check"


def _load_whisper_model():
    """Lazy load faster-whisper model"""
    global whisper_model
    if whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            whisper_model = WhisperModel(
                "base",
                device="cpu",
                compute_type="int8"
            )
            print("[SpeechAnalysis] Whisper model loaded successfully")
        except Exception as e:
            print(f"[SpeechAnalysis] Failed to load Whisper model: {e}")
            whisper_model = None
    return whisper_model


def _load_emotion_classifier():
    """Lazy load emotion classification pipeline"""
    global emotion_classifier
    if emotion_classifier is None:
        try:
            from transformers import pipeline
            emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True
            )
            print("[SpeechAnalysis] Emotion classifier loaded successfully")
        except Exception as e:
            print(f"[SpeechAnalysis] Failed to load emotion classifier: {e}")
            emotion_classifier = None
    return emotion_classifier


@dataclass
class GrammarIssue:
    """Grammar issue detected in speech"""
    message: str
    offset: int
    length: int
    replacements: List[str] = field(default_factory=list)
    rule_id: str = ""


@dataclass
class EmotionScore:
    """Emotion score from text analysis"""
    label: str
    score: float


@dataclass
class SpeechMetrics:
    """Complete speech analysis metrics"""
    # Transcription
    transcription: str = ""
    word_count: int = 0
    
    # Grammar
    grammar_issues: List[GrammarIssue] = field(default_factory=list)
    grammar_error_count: int = 0
    
    # Emotions
    emotions: List[EmotionScore] = field(default_factory=list)
    dominant_emotion: str = "neutral"
    dominant_emotion_score: float = 0.0
    
    # Fillers
    filler_count: int = 0
    filler_words: List[str] = field(default_factory=list)
    
    # Timing
    timestamp: float = 0.0


# Common filler words to detect
FILLER_WORDS = {
    "um", "uh", "er", "ah", "like", "you know", "actually", 
    "basically", "literally", "right", "okay", "so", "well",
    "i mean", "kind of", "sort of"
}


class SpeechAnalyzer:
    """
    Real-time speech analysis with:
    - Speech-to-text (faster-whisper)
    - Grammar checking (LanguageTool)
    - Emotion detection from text
    - Filler word detection
    """
    
    def __init__(self, history_size: int = 50):
        self.transcription_history: deque = deque(maxlen=history_size)
        self.emotion_history: deque = deque(maxlen=history_size)
        self.total_filler_count: int = 0
        self.total_word_count: int = 0
        self.total_grammar_errors: int = 0
        self._is_initialized = False
    
    def initialize(self):
        """Initialize models (can be called explicitly to avoid cold start)"""
        if not self._is_initialized:
            _load_whisper_model()
            _load_emotion_classifier()
            self._is_initialized = True
    
    def transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio file to text using Whisper"""
        model = _load_whisper_model()
        if model is None:
            return ""
        
        try:
            segments, info = model.transcribe(audio_path)
            text = " ".join([segment.text for segment in segments])
            return text.strip()
        except Exception as e:
            print(f"[SpeechAnalysis] Transcription error: {e}")
            return ""
    
    def check_grammar(self, text: str) -> List[GrammarIssue]:
        """Check grammar using LanguageTool"""
        if not text.strip():
            return []
        
        import requests
        
        try:
            # Try local LanguageTool server first
            try:
                resp = requests.post(
                    f"{LT_LOCAL_SERVER}/v2/check",
                    data={"text": text, "language": "en-US"},
                    timeout=5
                )
                data = resp.json()
            except requests.exceptions.ConnectionError:
                # Fallback to public API
                resp = requests.post(
                    LT_PUBLIC_API,
                    data={"text": text, "language": "en-US"},
                    timeout=10
                )
                data = resp.json()
            
            issues = []
            for match in data.get("matches", []):
                issue = GrammarIssue(
                    message=match.get("message", ""),
                    offset=match.get("offset", 0),
                    length=match.get("length", 0),
                    replacements=[r.get("value", "") for r in match.get("replacements", [])[:3]],
                    rule_id=match.get("rule", {}).get("id", "")
                )
                issues.append(issue)
            
            return issues
            
        except Exception as e:
            print(f"[SpeechAnalysis] Grammar check error: {e}")
            return []
    
    def analyze_emotions(self, text: str) -> List[EmotionScore]:
        """Analyze emotions from text"""
        if not text.strip():
            return []
        
        classifier = _load_emotion_classifier()
        if classifier is None:
            return []
        
        try:
            results = classifier(text[:512])  # Limit text length
            emotions = []
            
            if results and len(results) > 0:
                for emotion in results[0]:
                    emotions.append(EmotionScore(
                        label=emotion["label"],
                        score=float(emotion["score"])
                    ))
            
            return sorted(emotions, key=lambda x: x.score, reverse=True)
            
        except Exception as e:
            print(f"[SpeechAnalysis] Emotion analysis error: {e}")
            return []
    
    def detect_fillers(self, text: str) -> Tuple[int, List[str]]:
        """Detect filler words in text"""
        if not text:
            return 0, []
        
        text_lower = text.lower()
        found_fillers = []
        
        for filler in FILLER_WORDS:
            count = text_lower.count(filler)
            if count > 0:
                found_fillers.extend([filler] * count)
        
        return len(found_fillers), found_fillers
    
    def analyze_audio_bytes(self, audio_bytes: bytes, timestamp: float = 0.0) -> SpeechMetrics:
        """Analyze audio from bytes (base64 decoded)"""
        metrics = SpeechMetrics(timestamp=timestamp)
        
        # Save to temp file for whisper
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name
        
        try:
            # 1. Transcribe
            text = self.transcribe_audio(temp_path)
            metrics.transcription = text
            metrics.word_count = len(text.split()) if text else 0
            self.total_word_count += metrics.word_count
            
            if text:
                # Store in history
                self.transcription_history.append(text)
                
                # 2. Grammar check
                grammar_issues = self.check_grammar(text)
                metrics.grammar_issues = grammar_issues
                metrics.grammar_error_count = len(grammar_issues)
                self.total_grammar_errors += metrics.grammar_error_count
                
                # 3. Emotion analysis
                emotions = self.analyze_emotions(text)
                metrics.emotions = emotions
                if emotions:
                    metrics.dominant_emotion = emotions[0].label
                    metrics.dominant_emotion_score = emotions[0].score
                    self.emotion_history.append((emotions[0].label, emotions[0].score))
                
                # 4. Filler detection
                filler_count, filler_words = self.detect_fillers(text)
                metrics.filler_count = filler_count
                metrics.filler_words = filler_words
                self.total_filler_count += filler_count
        
        finally:
            # Cleanup temp file
            try:
                os.unlink(temp_path)
            except:
                pass
        
        return metrics
    
    def reset(self):
        """Reset session for new recording"""
        self.transcription_history.clear()
        self.emotion_history.clear()
        self.total_filler_count = 0
        self.total_word_count = 0
        self.total_grammar_errors = 0
    
    def get_session_summary(self) -> Dict:
        """Get summary statistics for the session"""
        # Calculate dominant emotion from history
        emotion_counts: Dict[str, int] = {}
        for emotion, _ in self.emotion_history:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        dominant = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else "neutral"
        
        return {
            "total_words": self.total_word_count,
            "total_fillers": self.total_filler_count,
            "filler_rate": (self.total_filler_count / max(self.total_word_count, 1)) * 100,
            "total_grammar_errors": self.total_grammar_errors,
            "dominant_emotion": dominant,
            "transcriptions_count": len(self.transcription_history),
            "full_transcription": " ".join(self.transcription_history)
        }


# Singleton instance
_speech_analyzer: Optional[SpeechAnalyzer] = None


def get_speech_analyzer() -> SpeechAnalyzer:
    """Get or create singleton analyzer"""
    global _speech_analyzer
    if _speech_analyzer is None:
        _speech_analyzer = SpeechAnalyzer()
    return _speech_analyzer


async def analyze_audio_async(audio_base64: str, timestamp: float = 0.0) -> Dict:
    """Async audio analysis for WebSocket"""
    loop = asyncio.get_event_loop()
    analyzer = get_speech_analyzer()
    
    # Decode base64 audio
    try:
        if ',' in audio_base64:
            audio_base64 = audio_base64.split(',')[1]
        audio_bytes = base64.b64decode(audio_base64)
    except Exception as e:
        return {"error": f"Failed to decode audio: {e}"}
    
    # Run analysis in executor to not block
    metrics = await loop.run_in_executor(
        None,
        analyzer.analyze_audio_bytes,
        audio_bytes,
        timestamp
    )
    
    return {
        "timestamp": metrics.timestamp,
        "transcription": metrics.transcription,
        "word_count": metrics.word_count,
        "grammar_issues": [
            {
                "message": issue.message,
                "offset": issue.offset,
                "length": issue.length,
                "replacements": issue.replacements
            }
            for issue in metrics.grammar_issues
        ],
        "grammar_error_count": metrics.grammar_error_count,
        "emotions": [
            {"label": e.label, "score": e.score}
            for e in metrics.emotions[:5]  # Top 5 emotions
        ],
        "dominant_emotion": metrics.dominant_emotion,
        "dominant_emotion_score": metrics.dominant_emotion_score,
        "filler_count": metrics.filler_count,
        "filler_words": metrics.filler_words
    }
