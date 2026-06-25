import re
import time
from typing import Dict, Any, Optional


class SpeechEngine:
    """
    Server-side speech analysis engine.
    Uses faster-whisper for transcription and computes acoustic metrics.
    """

    # Common English filler words
    FILLER_WORDS = {
        "um", "uh", "like", "you know", "basically", "literally",
        "actually", "sort of", "kind of", "right", "okay", "so"
    }

    def __init__(self):
        self._model = None

    def _get_model(self):
        """Lazy-load faster-whisper model to avoid heavy startup cost."""
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
                # Use "base" model for speed; swap to "medium"/"large-v3" in production
                self._model = WhisperModel("base", device="cpu", compute_type="int8")
            except ImportError:
                raise RuntimeError(
                    "faster-whisper is not installed. "
                    "Run: pip install faster-whisper"
                )
        return self._model

    def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribes audio file using faster-whisper.
        
        Args:
            audio_path: Absolute path to the audio file (.wav, .mp3, etc.)
            
        Returns:
            Dict with 'transcription', 'language', and 'duration_seconds'
        """
        model = self._get_model()
        start = time.perf_counter()
        segments, info = model.transcribe(audio_path, beam_size=5)
        elapsed = time.perf_counter() - start

        full_text = " ".join(segment.text.strip() for segment in segments)
        return {
            "transcription": full_text.strip(),
            "language": info.language,
            "language_probability": round(info.language_probability, 3),
            "duration_seconds": round(info.duration, 2),
            "transcription_time_seconds": round(elapsed, 2),
        }

    def compute_metrics(self, transcription: str, duration_seconds: float) -> Dict[str, Any]:
        """
        Computes acoustic metrics from a transcription and audio duration.
        
        Returns:
            Dict with wpm, filler_count, filler_rate, pause_estimate
        """
        words = transcription.split()
        word_count = len(words)

        # Words per minute
        minutes = duration_seconds / 60.0
        wpm = round(word_count / minutes, 1) if minutes > 0 else 0

        # Filler word detection
        normalized = transcription.lower()
        filler_count = 0
        filler_instances = []
        for filler in self.FILLER_WORDS:
            # Match whole word, case-insensitive
            pattern = rf"\b{re.escape(filler)}\b"
            matches = re.findall(pattern, normalized)
            if matches:
                filler_count += len(matches)
                filler_instances.append({"word": filler, "count": len(matches)})

        filler_rate = round((filler_count / word_count) * 100, 1) if word_count > 0 else 0

        # Pause estimate: rough heuristic based on WPM deviation from optimal (120-150 WPM)
        if wpm < 80:
            pace_label = "too_slow"
        elif wpm > 180:
            pace_label = "too_fast"
        else:
            pace_label = "optimal"

        # Fluency score: starts at 100, penalizes filler rate and pace
        fluency_score = 100
        fluency_score -= min(filler_rate * 2, 40)  # Cap filler penalty at 40 pts
        if pace_label != "optimal":
            fluency_score -= 10
        fluency_score = max(0, round(fluency_score))

        return {
            "word_count": word_count,
            "duration_seconds": duration_seconds,
            "wpm": wpm,
            "pace_label": pace_label,
            "filler_count": filler_count,
            "filler_rate_percent": filler_rate,
            "filler_instances": filler_instances,
            "fluency_score": fluency_score,
        }

    def analyze(self, audio_path: str) -> Dict[str, Any]:
        """
        Full pipeline: transcribe then compute metrics.
        Single entry point for Celery tasks.
        
        Returns:
            Combined dict of transcription + metrics
        """
        transcription_result = self.transcribe_audio(audio_path)
        metrics = self.compute_metrics(
            transcription=transcription_result["transcription"],
            duration_seconds=transcription_result["duration_seconds"],
        )
        return {**transcription_result, **metrics}
