"""
Filler Word Detection Module
Detects filler words, hesitations, and disfluencies in speech
"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import Counter
import re


@dataclass
class FillerInstance:
    """Represents a detected filler word instance"""
    word: str
    start: float
    end: float
    confidence: float
    category: str  # filler, hedge, discourse_marker


@dataclass
class FillerAnalysis:
    """Complete filler word analysis results"""
    instances: List[FillerInstance]
    total_count: int
    filler_rate_per_minute: float
    category_counts: Dict[str, int]
    most_common: List[Tuple[str, int]]
    severity: str  # low, moderate, high, very_high
    recommendations: List[str]


# Categorized filler words and hesitation markers
FILLER_CATEGORIES = {
    "filler": [
        "um", "uh", "er", "ah", "eh", "hmm", "hm", "mm",
        "umm", "uhh", "err", "ahh", "ehh"
    ],
    "hedge": [
        "like", "you know", "kind of", "sort of", "kinda", "sorta",
        "i mean", "i guess", "i think", "maybe", "probably",
        "basically", "essentially", "literally"
    ],
    "discourse_marker": [
        "so", "well", "actually", "honestly", "anyway", "anyways",
        "right", "okay", "ok", "yeah", "yes", "no"
    ],
    "repetition_starter": [
        "i i", "the the", "a a", "and and", "but but",
        "to to", "that that", "is is", "was was"
    ]
}

# Flatten for quick lookup
ALL_FILLERS = set()
FILLER_TO_CATEGORY = {}
for category, words in FILLER_CATEGORIES.items():
    for word in words:
        ALL_FILLERS.add(word)
        FILLER_TO_CATEGORY[word] = category


def normalize_word(word: str) -> str:
    """Normalize word for filler detection"""
    return word.lower().strip().strip(".,!?;:'\"")


def detect_fillers(
    transcript: str,
    timestamps: List[Dict],
    include_discourse_markers: bool = True
) -> List[FillerInstance]:
    """
    Detect filler words in transcript with timestamps.
    
    Args:
        transcript: Full text transcript
        timestamps: Word-level timestamps from ASR
        include_discourse_markers: Whether to include discourse markers like "so", "well"
        
    Returns:
        List of detected filler instances with timestamps
    """
    fillers = []
    
    # Categories to include
    categories_to_check = {"filler", "hedge", "repetition_starter"}
    if include_discourse_markers:
        categories_to_check.add("discourse_marker")
    
    # Check each word
    for i, word_info in enumerate(timestamps):
        word = normalize_word(word_info.get("word", ""))
        
        if word in FILLER_TO_CATEGORY:
            category = FILLER_TO_CATEGORY[word]
            if category in categories_to_check:
                fillers.append(FillerInstance(
                    word=word,
                    start=word_info.get("start", 0.0),
                    end=word_info.get("end", 0.0),
                    confidence=word_info.get("confidence", 1.0),
                    category=category
                ))
        
        # Check for two-word fillers (e.g., "you know", "kind of")
        if i + 1 < len(timestamps):
            next_word = normalize_word(timestamps[i + 1].get("word", ""))
            two_word = f"{word} {next_word}"
            if two_word in FILLER_TO_CATEGORY:
                category = FILLER_TO_CATEGORY[two_word]
                if category in categories_to_check:
                    fillers.append(FillerInstance(
                        word=two_word,
                        start=word_info.get("start", 0.0),
                        end=timestamps[i + 1].get("end", 0.0),
                        confidence=min(
                            word_info.get("confidence", 1.0),
                            timestamps[i + 1].get("confidence", 1.0)
                        ),
                        category=category
                    ))
        
        # Check for repetitions (word stutters)
        if i + 1 < len(timestamps):
            next_word = normalize_word(timestamps[i + 1].get("word", ""))
            if word == next_word and len(word) > 1:
                fillers.append(FillerInstance(
                    word=f"{word} {next_word}",
                    start=word_info.get("start", 0.0),
                    end=timestamps[i + 1].get("end", 0.0),
                    confidence=1.0,
                    category="repetition_starter"
                ))
    
    return fillers


def detect_hesitation_patterns(
    transcript: str,
    timestamps: List[Dict]
) -> List[Dict]:
    """
    Detect hesitation patterns beyond simple filler words.
    
    Args:
        transcript: Full text transcript
        timestamps: Word-level timestamps
        
    Returns:
        List of hesitation pattern occurrences
    """
    patterns = []
    
    # Detect long pauses between words (if timing available)
    for i in range(len(timestamps) - 1):
        current_end = timestamps[i].get("end", 0.0)
        next_start = timestamps[i + 1].get("start", 0.0)
        pause_duration = next_start - current_end
        
        if pause_duration > 0.5:  # Half second pause
            patterns.append({
                "type": "long_pause",
                "start": current_end,
                "end": next_start,
                "duration": pause_duration,
                "context": f"...{timestamps[i].get('word', '')} [pause] {timestamps[i+1].get('word', '')}..."
            })
    
    # Detect word elongations (if present in transcript)
    elongation_pattern = r'\b(\w)\1{2,}\b'  # repeated letters
    for match in re.finditer(elongation_pattern, transcript.lower()):
        patterns.append({
            "type": "elongation",
            "word": match.group(),
            "start": 0.0,  # Would need alignment
            "end": 0.0
        })
    
    return patterns


def calculate_filler_rate(fillers: List[FillerInstance], total_duration: float) -> float:
    """
    Calculate fillers per minute.
    
    Args:
        fillers: List of detected filler instances
        total_duration: Total audio/speech duration in seconds
        
    Returns:
        Filler rate per minute
    """
    if total_duration <= 0:
        return 0.0
    return len(fillers) / (total_duration / 60)


def analyze_fillers(
    transcript: str,
    timestamps: List[Dict],
    total_duration: float,
    include_discourse_markers: bool = False
) -> FillerAnalysis:
    """
    Perform complete filler word analysis.
    
    Args:
        transcript: Full text transcript
        timestamps: Word-level timestamps from ASR
        total_duration: Total speech duration in seconds
        include_discourse_markers: Include "so", "well", etc.
        
    Returns:
        Complete FillerAnalysis result
    """
    # Detect fillers
    instances = detect_fillers(transcript, timestamps, include_discourse_markers)
    
    # Calculate rate
    filler_rate = calculate_filler_rate(instances, total_duration)
    
    # Count by category
    category_counts = Counter(f.category for f in instances)
    
    # Most common fillers
    word_counts = Counter(f.word for f in instances)
    most_common = word_counts.most_common(5)
    
    # Determine severity
    if filler_rate < 2:
        severity = "low"
    elif filler_rate < 5:
        severity = "moderate"
    elif filler_rate < 10:
        severity = "high"
    else:
        severity = "very_high"
    
    # Generate recommendations
    recommendations = generate_filler_recommendations(
        instances, filler_rate, category_counts, most_common
    )
    
    return FillerAnalysis(
        instances=instances,
        total_count=len(instances),
        filler_rate_per_minute=filler_rate,
        category_counts=dict(category_counts),
        most_common=most_common,
        severity=severity,
        recommendations=recommendations
    )


def generate_filler_recommendations(
    instances: List[FillerInstance],
    filler_rate: float,
    category_counts: Dict[str, int],
    most_common: List[Tuple[str, int]]
) -> List[str]:
    """
    Generate actionable recommendations based on filler analysis.
    
    Args:
        instances: List of filler instances
        filler_rate: Fillers per minute
        category_counts: Counts by category
        most_common: Most common filler words
        
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    if filler_rate >= 10:
        recommendations.append(
            "Your filler word rate is very high. Practice pausing silently "
            "instead of saying 'um' or 'uh' when gathering your thoughts."
        )
    elif filler_rate >= 5:
        recommendations.append(
            "Try to reduce filler words by taking brief silent pauses instead. "
            "This makes you appear more confident and thoughtful."
        )
    
    # Specific recommendations by category
    if category_counts.get("filler", 0) > 5:
        recommendations.append(
            "Practice replacing 'um' and 'uh' with silent pauses. "
            "Record yourself and review to build awareness."
        )
    
    if category_counts.get("hedge", 0) > 3:
        recommendations.append(
            "Reduce hedging words like 'kind of', 'sort of', 'basically'. "
            "These undermine the strength of your statements."
        )
    
    if category_counts.get("repetition_starter", 0) > 2:
        recommendations.append(
            "You're repeating words at the start of phrases. "
            "Slow down and take a breath before speaking."
        )
    
    # Most common word
    if most_common and most_common[0][1] > 5:
        word, count = most_common[0]
        recommendations.append(
            f"You said '{word}' {count} times. "
            f"Be mindful of this habit and practice alternatives."
        )
    
    if not recommendations:
        recommendations.append(
            "Great job! Your filler word usage is minimal. "
            "Continue practicing to maintain this level."
        )
    
    return recommendations


def get_filler_timeline(
    instances: List[FillerInstance],
    total_duration: float,
    bucket_size: float = 30.0
) -> List[Dict]:
    """
    Create a timeline of filler frequency over time.
    
    Args:
        instances: List of filler instances
        total_duration: Total duration in seconds
        bucket_size: Size of each time bucket in seconds
        
    Returns:
        List of time buckets with filler counts
    """
    if total_duration <= 0:
        return []
    
    num_buckets = int(total_duration / bucket_size) + 1
    buckets = [{"start": i * bucket_size, "end": (i + 1) * bucket_size, "count": 0} 
               for i in range(num_buckets)]
    
    for filler in instances:
        bucket_idx = int(filler.start / bucket_size)
        if 0 <= bucket_idx < len(buckets):
            buckets[bucket_idx]["count"] += 1
    
    return buckets
