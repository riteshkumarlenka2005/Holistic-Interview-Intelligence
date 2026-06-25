"""
Prosody Analysis Module
Analyzes speech patterns including pitch, pace, tone, and energy using librosa
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np

# Lazy imports
librosa = None
scipy_signal = None


def _load_librosa():
    """Lazy load librosa"""
    global librosa, scipy_signal
    if librosa is None:
        try:
            import librosa as _librosa
            from scipy import signal as _signal
            librosa = _librosa
            scipy_signal = _signal
        except ImportError:
            raise ImportError("librosa and scipy required: pip install librosa scipy")
    return librosa


@dataclass
class PitchAnalysis:
    """Pitch (F0) analysis results"""
    mean: float
    std: float
    min: float
    max: float
    range: float
    variability: str  # low, moderate, high
    contour: List[float]  # pitch over time


@dataclass
class PaceAnalysis:
    """Speaking pace analysis"""
    words_per_minute: float
    syllables_per_second: float
    assessment: str  # slow, normal, fast
    pauses: List[Dict]  # list of pause info
    total_pause_duration: float
    speech_to_pause_ratio: float


@dataclass
class EnergyAnalysis:
    """Energy/loudness analysis"""
    mean_rms: float
    max_rms: float
    min_rms: float
    dynamic_range_db: float
    variation: str  # low, moderate, high
    energy_contour: List[float]


@dataclass
class ToneAnalysis:
    """Overall tone analysis"""
    overall: str  # confident, neutral, hesitant, nervous
    confidence_score: float
    monotone_score: float  # 0-1, higher = more monotone
    expressiveness: float  # 0-1, higher = more expressive


@dataclass
class ProsodyResult:
    """Complete prosody analysis result"""
    pitch: PitchAnalysis
    pace: PaceAnalysis
    energy: EnergyAnalysis
    tone: ToneAnalysis
    mfccs: Optional[np.ndarray]
    spectral_features: Dict


class ProsodyAnalyzer:
    """
    Comprehensive prosody analyzer using librosa.
    Extracts pitch, pace, energy, and tone features from audio.
    """
    
    def __init__(self, sample_rate: int = 16000):
        """
        Initialize prosody analyzer.
        
        Args:
            sample_rate: Expected audio sample rate
        """
        self.sample_rate = sample_rate
        _load_librosa()
    
    def load_audio(
        self,
        audio_path: str,
        target_sr: Optional[int] = None
    ) -> Tuple[np.ndarray, int]:
        """
        Load audio file.
        
        Args:
            audio_path: Path to audio file
            target_sr: Target sample rate (None uses file's native rate)
            
        Returns:
            Tuple of (audio_array, sample_rate)
        """
        y, sr = librosa.load(audio_path, sr=target_sr or self.sample_rate)
        return y, sr
    
    def analyze_pitch(
        self,
        y: np.ndarray,
        sr: int,
        fmin: float = 75.0,
        fmax: float = 600.0
    ) -> PitchAnalysis:
        """
        Analyze pitch (fundamental frequency) of audio.
        
        Args:
            y: Audio time series
            sr: Sample rate
            fmin: Minimum expected frequency (Hz)
            fmax: Maximum expected frequency (Hz)
            
        Returns:
            PitchAnalysis with pitch statistics
        """
        # Extract pitch using pyin algorithm
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y,
            fmin=fmin,
            fmax=fmax,
            sr=sr
        )
        
        # Filter to voiced regions only
        f0_voiced = f0[voiced_flag]
        
        if len(f0_voiced) == 0:
            return PitchAnalysis(
                mean=0.0, std=0.0, min=0.0, max=0.0,
                range=0.0, variability="unknown", contour=[]
            )
        
        mean_f0 = float(np.nanmean(f0_voiced))
        std_f0 = float(np.nanstd(f0_voiced))
        min_f0 = float(np.nanmin(f0_voiced))
        max_f0 = float(np.nanmax(f0_voiced))
        range_f0 = max_f0 - min_f0
        
        # Classify variability based on coefficient of variation
        cv = std_f0 / mean_f0 if mean_f0 > 0 else 0
        if cv < 0.1:
            variability = "low"
        elif cv < 0.25:
            variability = "moderate"
        else:
            variability = "high"
        
        # Downsample contour for storage
        contour_length = min(100, len(f0))
        indices = np.linspace(0, len(f0) - 1, contour_length, dtype=int)
        contour = [float(f0[i]) if not np.isnan(f0[i]) else 0.0 for i in indices]
        
        return PitchAnalysis(
            mean=mean_f0,
            std=std_f0,
            min=min_f0,
            max=max_f0,
            range=range_f0,
            variability=variability,
            contour=contour
        )
    
    def analyze_pace(
        self,
        y: np.ndarray,
        sr: int,
        word_timestamps: Optional[List[Dict]] = None,
        silence_threshold_db: float = -40.0
    ) -> PaceAnalysis:
        """
        Analyze speaking pace and pauses.
        
        Args:
            y: Audio time series
            sr: Sample rate
            word_timestamps: Optional word timing info from transcription
            silence_threshold_db: Threshold for silence detection
            
        Returns:
            PaceAnalysis with pace metrics
        """
        duration = len(y) / sr
        
        # Detect pauses using onset detection and energy
        rms = librosa.feature.rms(y=y)[0]
        rms_db = librosa.amplitude_to_db(rms, ref=np.max)
        
        # Find silent regions
        hop_length = 512
        frame_time = hop_length / sr
        is_silence = rms_db < silence_threshold_db
        
        pauses = []
        pause_start = None
        min_pause_duration = 0.2  # Minimum pause length in seconds
        
        for i, silent in enumerate(is_silence):
            if silent and pause_start is None:
                pause_start = i * frame_time
            elif not silent and pause_start is not None:
                pause_end = i * frame_time
                pause_duration = pause_end - pause_start
                if pause_duration >= min_pause_duration:
                    pauses.append({
                        "start": pause_start,
                        "end": pause_end,
                        "duration": pause_duration,
                        "type": "hesitation" if pause_duration < 0.5 else "natural"
                    })
                pause_start = None
        
        total_pause = sum(p["duration"] for p in pauses)
        speech_duration = duration - total_pause
        
        # Calculate words per minute from timestamps if available
        wpm = 0.0
        if word_timestamps and len(word_timestamps) > 0:
            word_count = len(word_timestamps)
            if speech_duration > 0:
                wpm = (word_count / speech_duration) * 60
        else:
            # Estimate using onset detection
            onsets = librosa.onset.onset_detect(y=y, sr=sr, units='time')
            estimated_syllables = len(onsets)
            sps = estimated_syllables / speech_duration if speech_duration > 0 else 0
            wpm = sps * 60 / 1.5  # Rough estimate: ~1.5 syllables per word
        
        # Assess pace
        if wpm < 100:
            assessment = "slow"
        elif wpm < 160:
            assessment = "normal"
        else:
            assessment = "fast"
        
        return PaceAnalysis(
            words_per_minute=wpm,
            syllables_per_second=wpm / 60 * 1.5,
            assessment=assessment,
            pauses=pauses,
            total_pause_duration=total_pause,
            speech_to_pause_ratio=speech_duration / total_pause if total_pause > 0 else float('inf')
        )
    
    def analyze_energy(self, y: np.ndarray, sr: int) -> EnergyAnalysis:
        """
        Analyze energy/loudness patterns.
        
        Args:
            y: Audio time series
            sr: Sample rate
            
        Returns:
            EnergyAnalysis with energy metrics
        """
        rms = librosa.feature.rms(y=y)[0]
        
        mean_rms = float(np.mean(rms))
        max_rms = float(np.max(rms))
        min_rms = float(np.min(rms[rms > 0])) if np.any(rms > 0) else 0.0
        
        # Dynamic range in dB
        if min_rms > 0:
            dynamic_range = 20 * np.log10(max_rms / min_rms)
        else:
            dynamic_range = 0.0
        
        # Energy variation (coefficient of variation)
        cv = float(np.std(rms) / mean_rms) if mean_rms > 0 else 0
        if cv < 0.2:
            variation = "low"
        elif cv < 0.4:
            variation = "moderate"
        else:
            variation = "high"
        
        # Downsample contour
        contour_length = min(100, len(rms))
        indices = np.linspace(0, len(rms) - 1, contour_length, dtype=int)
        energy_contour = [float(rms[i]) for i in indices]
        
        return EnergyAnalysis(
            mean_rms=mean_rms,
            max_rms=max_rms,
            min_rms=min_rms,
            dynamic_range_db=float(dynamic_range),
            variation=variation,
            energy_contour=energy_contour
        )
    
    def analyze_tone(
        self,
        pitch: PitchAnalysis,
        pace: PaceAnalysis,
        energy: EnergyAnalysis
    ) -> ToneAnalysis:
        """
        Analyze overall tone based on other prosodic features.
        
        Args:
            pitch: Pitch analysis results
            pace: Pace analysis results
            energy: Energy analysis results
            
        Returns:
            ToneAnalysis with tone classification
        """
        # Monotone score: low pitch variability = monotone
        monotone_score = 1.0 - min(1.0, pitch.std / 50)  # Normalize by typical std
        
        # Expressiveness: combination of pitch and energy variation
        pitch_expressiveness = {"low": 0.2, "moderate": 0.5, "high": 0.8}.get(pitch.variability, 0.5)
        energy_expressiveness = {"low": 0.2, "moderate": 0.5, "high": 0.8}.get(energy.variation, 0.5)
        expressiveness = (pitch_expressiveness + energy_expressiveness) / 2
        
        # Calculate confidence based on multiple factors
        confidence_factors = []
        
        # Steady pace indicates confidence
        pace_score = 0.7 if pace.assessment == "normal" else 0.4
        confidence_factors.append(pace_score)
        
        # Moderate energy variation indicates engagement
        energy_score = 0.7 if energy.variation == "moderate" else 0.4
        confidence_factors.append(energy_score)
        
        # Some pitch variation indicates confidence (not monotone or erratic)
        pitch_score = 0.8 if pitch.variability == "moderate" else 0.4
        confidence_factors.append(pitch_score)
        
        # Too many pauses may indicate hesitation
        pause_penalty = min(0.3, len(pace.pauses) * 0.02)
        
        confidence_score = np.mean(confidence_factors) - pause_penalty
        confidence_score = float(max(0, min(1, confidence_score)))
        
        # Classify overall tone
        if confidence_score >= 0.7:
            overall = "confident"
        elif confidence_score >= 0.5:
            overall = "neutral"
        elif pace.words_per_minute > 180 or len(pace.pauses) > 10:
            overall = "nervous"
        else:
            overall = "hesitant"
        
        return ToneAnalysis(
            overall=overall,
            confidence_score=confidence_score,
            monotone_score=float(monotone_score),
            expressiveness=float(expressiveness)
        )
    
    def extract_mfccs(
        self,
        y: np.ndarray,
        sr: int,
        n_mfcc: int = 13
    ) -> np.ndarray:
        """
        Extract MFCC features.
        
        Args:
            y: Audio time series
            sr: Sample rate
            n_mfcc: Number of MFCCs to extract
            
        Returns:
            MFCC features array
        """
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
        return mfccs
    
    def extract_spectral_features(self, y: np.ndarray, sr: int) -> Dict:
        """
        Extract additional spectral features.
        
        Args:
            y: Audio time series
            sr: Sample rate
            
        Returns:
            Dictionary of spectral features
        """
        # Spectral centroid - brightness
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        
        # Spectral bandwidth - spread
        bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        
        # Spectral rolloff
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        
        # Zero crossing rate - noisiness
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        
        return {
            "spectral_centroid_mean": float(np.mean(centroid)),
            "spectral_centroid_std": float(np.std(centroid)),
            "spectral_bandwidth_mean": float(np.mean(bandwidth)),
            "spectral_rolloff_mean": float(np.mean(rolloff)),
            "zero_crossing_rate_mean": float(np.mean(zcr))
        }
    
    def analyze(
        self,
        audio_path: str,
        word_timestamps: Optional[List[Dict]] = None,
        extract_mfcc: bool = True
    ) -> ProsodyResult:
        """
        Perform complete prosody analysis on audio file.
        
        Args:
            audio_path: Path to audio file
            word_timestamps: Optional word timing info
            extract_mfcc: Whether to extract MFCC features
            
        Returns:
            Complete ProsodyResult
        """
        y, sr = self.load_audio(audio_path)
        return self.analyze_audio(y, sr, word_timestamps, extract_mfcc)
    
    def analyze_audio(
        self,
        y: np.ndarray,
        sr: int,
        word_timestamps: Optional[List[Dict]] = None,
        extract_mfcc: bool = True
    ) -> ProsodyResult:
        """
        Perform complete prosody analysis on audio array.
        
        Args:
            y: Audio time series
            sr: Sample rate
            word_timestamps: Optional word timing info
            extract_mfcc: Whether to extract MFCC features
            
        Returns:
            Complete ProsodyResult
        """
        pitch = self.analyze_pitch(y, sr)
        pace = self.analyze_pace(y, sr, word_timestamps)
        energy = self.analyze_energy(y, sr)
        tone = self.analyze_tone(pitch, pace, energy)
        
        mfccs = self.extract_mfccs(y, sr) if extract_mfcc else None
        spectral = self.extract_spectral_features(y, sr)
        
        return ProsodyResult(
            pitch=pitch,
            pace=pace,
            energy=energy,
            tone=tone,
            mfccs=mfccs,
            spectral_features=spectral
        )


def analyze_prosody(audio_features: Dict) -> Dict:
    """
    Legacy function - analyze prosodic features of speech.
    Maintained for backward compatibility.
    
    Args:
        audio_features: Extracted audio features (or audio path under 'path' key)
        
    Returns:
        Prosody analysis results as dictionary
    """
    analyzer = ProsodyAnalyzer()
    
    if "path" in audio_features:
        result = analyzer.analyze(audio_features["path"])
    elif "audio" in audio_features and "sr" in audio_features:
        result = analyzer.analyze_audio(
            audio_features["audio"],
            audio_features["sr"]
        )
    else:
        # Return placeholder for incomplete input
        return {
            "pitch": {
                "mean": 0.0, "std": 0.0, "range": [0.0, 0.0],
                "variability": "unknown"
            },
            "pace": {"words_per_minute": 0.0, "assessment": "unknown", "pauses": []},
            "energy": {"mean": 0.0, "variation": "unknown"},
            "tone": {"overall": "unknown", "confidence": 0.0}
        }
    
    return {
        "pitch": {
            "mean": result.pitch.mean,
            "std": result.pitch.std,
            "range": [result.pitch.min, result.pitch.max],
            "variability": result.pitch.variability
        },
        "pace": {
            "words_per_minute": result.pace.words_per_minute,
            "assessment": result.pace.assessment,
            "pauses": result.pace.pauses
        },
        "energy": {
            "mean": result.energy.mean_rms,
            "variation": result.energy.variation
        },
        "tone": {
            "overall": result.tone.overall,
            "confidence": result.tone.confidence_score
        }
    }


def calculate_speaking_pace(word_timestamps: List[Dict]) -> float:
    """Calculate speaking pace in words per minute from word timestamps."""
    if not word_timestamps:
        return 0.0
    
    total_words = len(word_timestamps)
    start_time = word_timestamps[0].get("start", 0)
    end_time = word_timestamps[-1].get("end", 0)
    duration_minutes = (end_time - start_time) / 60
    
    return total_words / duration_minutes if duration_minutes > 0 else 0.0
