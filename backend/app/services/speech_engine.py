"""
Speech Intelligence Engine (Phase 4)
Deterministic acoustic and speech metric analysis using faster-whisper.
Extracts timestamps, pauses, fillers, wpm, and structured events.
"""
import re
import time
from typing import Dict, Any, List, Optional
import numpy as np

class SpeechIntelligenceEngine:
    # Common English filler words
    FILLER_WORDS = {
        "um", "uh", "like", "you know", "basically", "literally",
        "actually", "sort of", "kind of", "right", "okay", "so"
    }
    
    # Heuristics
    LONG_PAUSE_THRESHOLD_MS = 1500  # 1.5 seconds

    def __init__(self):
        self._model = None

    def _get_model(self):
        """Lazy-load faster-whisper model."""
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
                self._model = WhisperModel("base", device="cpu", compute_type="int8")
            except ImportError:
                raise RuntimeError("faster-whisper is not installed.")
        return self._model

    def analyze_audio(self, audio_path: str, is_partial: bool = False) -> Dict[str, Any]:
        """
        Transcribes audio and extracts deterministic metrics.
        Returns the definitive SpeechMetrics JSON object.
        """
        model = self._get_model()
        
        # Word timestamps are strictly required for our deterministic metrics
        segments_generator, info = model.transcribe(
            audio_path, 
            beam_size=5,
            word_timestamps=True
        )
        
        segments = list(segments_generator)
        
        # We will build the metrics progressively
        transcript_parts = []
        word_timestamps = []
        segment_metrics = []
        events = []
        
        filler_counts = {word: 0 for word in self.FILLER_WORDS}
        total_filler_count = 0
        restart_count = 0
        
        # Accumulate data
        for segment in segments:
            transcript_parts.append(segment.text.strip())
            
            segment_start_ms = int(segment.start * 1000)
            segment_end_ms = int(segment.end * 1000)
            segment_words = []
            
            for word in segment.words:
                w_start_ms = int(word.start * 1000)
                w_end_ms = int(word.end * 1000)
                clean_word = word.word.strip()
                
                word_obj = {
                    "word": clean_word,
                    "start_ms": w_start_ms,
                    "end_ms": w_end_ms
                }
                word_timestamps.append(word_obj)
                segment_words.append(word_obj)
                
                # Check fillers
                clean_lower = clean_word.lower().strip(",.!?")
                if clean_lower in self.FILLER_WORDS:
                    filler_counts[clean_lower] += 1
                    total_filler_count += 1
                    events.append({
                        "time": w_start_ms,
                        "type": "FILLER_WORD",
                        "word": clean_lower
                    })
                
                # Check Restarts (heuristic: "I... I..." or "so... so...")
                # We will do a basic check here or globally. Let's do a global pass later.

            segment_metrics.append({
                "start": segment_start_ms,
                "end": segment_end_ms,
                "text": segment.text.strip(),
                # We can calculate WPM and clarity per segment if desired
            })

        full_transcript = " ".join(transcript_parts)
        
        # ---------------------------------------------------------
        # Calculate Acoustic Metrics mathematically
        # ---------------------------------------------------------
        total_duration_ms = 0
        if word_timestamps:
            total_duration_ms = word_timestamps[-1]["end_ms"] - word_timestamps[0]["start_ms"]
        
        # Count pauses by looking at gaps between words
        pauses = []
        for i in range(1, len(word_timestamps)):
            prev_word = word_timestamps[i-1]
            curr_word = word_timestamps[i]
            gap_ms = curr_word["start_ms"] - prev_word["end_ms"]
            
            if gap_ms > 300: # Any gap > 300ms is considered a pause
                pauses.append(gap_ms)
                if gap_ms >= self.LONG_PAUSE_THRESHOLD_MS:
                    events.append({
                        "time": prev_word["end_ms"],
                        "type": "LONG_PAUSE",
                        "duration_ms": gap_ms
                    })
                    
        # Basic Restart detection (repeated exact words or common restart phrases)
        words_only = [w["word"].lower().strip(",.!?") for w in word_timestamps]
        for i in range(1, len(words_only)):
            if words_only[i] == words_only[i-1] and len(words_only[i]) > 1:
                # E.g. "I I", "we we", "because because"
                restart_count += 1
                events.append({
                    "time": word_timestamps[i]["start_ms"],
                    "type": "RESTART"
                })

        # Aggregations
        word_count = len(word_timestamps)
        wpm = 0.0
        if total_duration_ms > 0:
            minutes = total_duration_ms / 60000.0
            wpm = round(word_count / minutes, 1)
            
        pause_count = len(pauses)
        average_pause_ms = int(np.mean(pauses)) if pauses else 0
        longest_pause_ms = int(max(pauses)) if pauses else 0
        silence_duration_ms = sum(pauses)
        
        # Speaking ratio
        speaking_ratio = 1.0
        if total_duration_ms > 0:
            speaking_ratio = round((total_duration_ms - silence_duration_ms) / total_duration_ms, 2)
            
        # Segment-level WPM
        for seg in segment_metrics:
            seg_dur = seg["end"] - seg["start"]
            seg_words = len(seg["text"].split())
            if seg_dur > 0:
                seg["wpm"] = round(seg_words / (seg_dur / 60000.0), 1)
            else:
                seg["wpm"] = 0.0
            seg["clarity"] = 0.95 # Mock for now until we pull token-level probabilities if available

        # Filter out 0 count fillers
        active_fillers = {k: v for k, v in filler_counts.items() if v > 0}

        # ---------------------------------------------------------
        # Deterministic Speech Score Heuristic
        # ---------------------------------------------------------
        # Start at 100, penalize for bad metrics
        score = 100.0
        
        # Penalty: Fillers
        filler_rate = (total_filler_count / word_count) if word_count > 0 else 0
        score -= min(filler_rate * 500, 30) # Max 30 pt penalty for high fillers
        
        # Penalty: Restarts
        score -= min(restart_count * 2.0, 15)
        
        # Penalty: Too slow or too fast
        if wpm < 110:
            score -= min((110 - wpm) * 0.5, 20)
        elif wpm > 180:
            score -= min((wpm - 180) * 0.5, 20)
            
        # Penalty: Speaking ratio (Too much silence)
        if speaking_ratio < 0.60:
            score -= 10
            
        speech_score = max(0.0, round(score, 1))

        # Sort events by time
        events.sort(key=lambda x: x["time"])

        return {
            "schema_version": "1.0",
            "partial": is_partial,
            "transcript": full_transcript,
            "transcription_confidence": round(info.language_probability, 2),
            "speech_score": speech_score,
            "metrics": {
                "wpm": wpm,
                "speech_duration_ms": total_duration_ms,
                "silence_duration_ms": silence_duration_ms,
                "speaking_ratio": speaking_ratio,
                "pause_count": pause_count,
                "average_pause_ms": average_pause_ms,
                "longest_pause_ms": longest_pause_ms,
                "restart_count": restart_count,
                "filler_words": active_fillers,
                "clarity": 0.95 # Overall average
            },
            "timestamps": word_timestamps,
            "segments": segment_metrics,
            "events": events
        }
