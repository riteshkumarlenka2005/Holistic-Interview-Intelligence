"""
Demo 2: DeepFace Emotion Intelligence Engine — Production Quality
=================================================================
Philosophy: DeepFace is a signal provider, not the decision-maker.
            This module is a Facial Emotion Interpreter — it converts
            raw facial affect into interview-relevant states.
            Final Confidence Score belongs to the Holistic Confidence
            Engine (MediaPipe + DeepFace + Whisper + Gemini).

Features:
  - Background thread    : DeepFace at 4 FPS, display at full 30 FPS
  - Temporal smoothing   : EMA eliminates single-frame flicker
  - State debouncing     : Requires 3 consecutive cycles (0.75s) to change state
  - Candidate locking    : largest/closest face — matches MediaPipe
  - Emotion Quality Gate : blur / brightness / face-area check
  - Facial Emotion Interp: 10 states (Positive, Neutral, Attention Risk)
  - Configurable profiles: technical, behavioral, general weights
  - Stability & Engage   : High-baseline engagement (80%) with EMA smoothing
  - HUD panel            : Dominant raw emotion, state confidence, color-coded emotion drift
  - Standardized JSON    : Outputs Holistic-compatible data dict structure

Install:  pip install deepface tf-keras opencv-python numpy
Run:      python demos/2_deepface_demo.py
Controls: Press 'q' to quit | 'r' to reset candidate lock
"""

import cv2
import math
import time
import threading
from collections import Counter, deque
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

DEEPFACE_BACKEND  = "opencv"      # "opencv" | "retinaface"
ANALYSIS_FPS      = 4
ANALYSIS_INTERVAL = 1.0 / ANALYSIS_FPS
EMA_ALPHA         = 0.30

MIN_FACE_AREA_RATIO   = 0.03
CANDIDATE_LOCK_FRAMES = 5

HISTORY_SECONDS   = 60
STABILITY_WINDOW  = 20
DEBOUNCE_CYCLES   = 3             # 3 cycles at 4 FPS = 0.75s

BLUR_THRESHOLD    = 60.0
DARK_THRESHOLD    = 40.0
QUALITY_GATE      = 0.45

ACTIVE_PROFILE    = "general"


# ── State Groups ─────────────────────────────────────────────────────────
POSITIVE_STATES = {"Confident", "Engaged", "Focused"}
NEUTRAL_STATES  = {"Calm", "Thinking"}
RISK_STATES     = {"Distracted", "Fatigued", "Confused", "Nervous", "Frustrated"}
ALL_STATES      = ["Calm", "Focused", "Thinking", "Engaged", "Confident",
                   "Nervous", "Confused", "Frustrated", "Fatigued", "Distracted"]

# ── Rolling Window Sizes (at ANALYSIS_FPS = 4) ──────────────────────────
THINKING_FRAMES    = 8    # ~2 seconds  — neutral plateaus + happy drops
FOCUSED_FRAMES     = 20   # ~5 seconds  — std dev of neutral < threshold
FATIGUED_BASELINE  = 300  # 5 min session baseline sampling window (seconds)
FATIGUED_FRAMES    = 20   # window used to compute current sad average


# ─────────────────────────────────────────────────────────────────────────────
# Colors
# ─────────────────────────────────────────────────────────────────────────────
FONT       = cv2.FONT_HERSHEY_SIMPLEX
GREEN      = (0, 220, 80)
YELLOW     = (0, 200, 255)
RED        = (0, 60, 230)
ORANGE     = (0, 140, 255)
CYAN       = (255, 200, 0)
GRAY       = (160, 160, 160)
WHITE      = (255, 255, 255)
DARK_PANEL = (20, 20, 20)

STATE_COLORS: dict[str, tuple[int, int, int]] = {
    "Confident":  GREEN,
    "Engaged":    GREEN,
    "Focused":    CYAN,
    "Calm":       CYAN,
    "Thinking":   YELLOW,
    "Distracted": GRAY,
    "Fatigued":   GRAY,
    "Confused":   ORANGE,
    "Nervous":    ORANGE,
    "Frustrated": RED,
}


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def apply_clahe(img: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    return cv2.cvtColor(cv2.merge((cl, a, b)), cv2.COLOR_LAB2BGR)


def open_camera():
    backends = [("DirectShow", cv2.CAP_DSHOW), ("MSMF", cv2.CAP_MSMF), ("Default", None)]
    for name, flag in backends:
        print(f"Trying camera backend: {name} ...")
        cap = cv2.VideoCapture(0, flag) if flag is not None else cv2.VideoCapture(0)
        if not cap.isOpened():
            continue
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        for _ in range(15): cap.read(); cv2.waitKey(30)
        ret, frame = cap.read()
        if ret and frame is not None and frame.mean() > 1.0:
            print(f"  [OK] Camera ready with {name}")
            return cap
        cap.release()
    return None


def entropy_confidence(probs: dict) -> float:
    values = np.array(list(probs.values()), dtype=float)
    values = values / (values.sum() + 1e-9)
    h = -float(np.sum(values * np.log(values + 1e-9)))
    h_max = math.log(len(values)) if len(values) > 1 else 1.0
    return round(1.0 - (h / h_max), 3)


# ─────────────────────────────────────────────────────────────────────────────
# Subsystems
# ─────────────────────────────────────────────────────────────────────────────
class EmotionQualityAssessor:
    def assess(self, frame: np.ndarray, region: dict, fw: int, fh: int) -> dict:
        x, y, w, h = region.get("x", 0), region.get("y", 0), region.get("w", 0), region.get("h", 0)
        _empty = {"score": 0.0, "blur": 0.0, "brightness": 0.0, "face_area": 0.0, "lighting": "Unknown", "blur_label": "Unknown"}

        if w < 10 or h < 10: return _empty
        face = frame[max(0, y):min(fh, y+h), max(0, x):min(fw, x+w)]
        if face.size == 0: return _empty

        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        blur_val = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        blur_score = min(1.0, blur_val / 200.0)

        lab = cv2.cvtColor(face, cv2.COLOR_BGR2LAB)
        brightness = float(cv2.mean(lab)[0])
        brightness_score = 1.0 - abs(brightness - 128.0) / 128.0

        face_area = (w * h) / max(fw * fh, 1)
        area_score = min(1.0, face_area / 0.05)

        score = 0.40 * blur_score + 0.35 * brightness_score + 0.25 * area_score

        lighting = "Too Dark" if brightness < DARK_THRESHOLD else "Overexposed" if brightness > 210 else "Good"
        blur_lbl = "Blurry" if blur_val < BLUR_THRESHOLD else "Acceptable" if blur_val < 150 else "Sharp"

        return {"score": round(score, 3), "blur": round(blur_val, 1), "brightness": round(brightness, 1),
                "face_area": round(face_area, 3), "lighting": lighting, "blur_label": blur_lbl}


class TemporalSmoother:
    LABELS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
    def __init__(self, alpha: float = EMA_ALPHA):
        self.alpha = alpha
        self._smoothed = {k: 0.0 for k in self.LABELS}
        self._init = False

    def update(self, raw_probs: dict) -> dict:
        if not self._init:
            self._smoothed = {k: raw_probs.get(k, 0.0) for k in self.LABELS}
            self._init = True
        else:
            for k in self.LABELS:
                self._smoothed[k] = (1 - self.alpha) * self._smoothed[k] + self.alpha * raw_probs.get(k, 0.0)
        return dict(self._smoothed)


class CandidateTracker:
    def __init__(self):
        self._locked_centre = None
        self._locked = False
        self._stable_count = 0

    @property
    def is_locked(self) -> bool: return self._locked

    def select(self, regions: list, fw: int, fh: int):
        area = lambda r: (r.get("w", 0) * r.get("h", 0)) / max(fw * fh, 1)
        centre = lambda r: ((r.get("x", 0) + r.get("w", 0)/2)/fw, (r.get("y", 0) + r.get("h", 0)/2)/fh)

        valid = [r for r in regions if area(r) >= MIN_FACE_AREA_RATIO]
        if not valid:
            self._stable_count = 0
            return None

        if not self._locked:
            best = max(valid, key=area)
            self._stable_count += 1
            if self._stable_count >= CANDIDATE_LOCK_FRAMES:
                self._locked_centre = centre(best)
                self._locked = True
            return best
        else:
            lcx, lcy = self._locked_centre
            best = min(valid, key=lambda r: math.hypot(centre(r)[0]-lcx, centre(r)[1]-lcy))
            cx, cy = centre(best)
            if math.hypot(cx-lcx, cy-lcy) > 0.20: return None
            self._locked_centre = (0.9 * lcx + 0.1 * cx, 0.9 * lcy + 0.1 * cy)
            return best

    def force_reset(self):
        self._locked_centre, self._locked, self._stable_count = None, False, 0


class BehavioralStateClassifier:
    """
    Rule-based + time-window emotion interpreter.

    Layer 1 — Simple mapping (single frame thresholds):
      Calm, Engaged, Confident, Nervous, Confused, Frustrated

    Layer 2 — Time-based mapping (rolling window analysis):
      Thinking : neutral stable 2s + happy drops to ~0
      Focused  : std-dev of neutral < 5 over 5s
      Fatigued : sad creeping above session baseline by 15%
      Distracted: face not detected by DeepFace

    Debounce: state must win DEBOUNCE_CYCLES consecutive analyses before switching.

    Integration hook: update_external() accepts MediaPipe signals.
    """

    # Rolling window: 40 slots at 4 FPS = 10 seconds
    WINDOW_SIZE = 40

    def __init__(self, debounce: int = DEBOUNCE_CYCLES):
        self._window: deque = deque(maxlen=self.WINDOW_SIZE)
        self._debounce_buf: deque = deque(maxlen=debounce)
        self._state  = "Calm"
        self._scores = {s: 0.0 for s in ALL_STATES}
        self._session_start   = time.time()
        self._sad_baseline    = None          # set from first 5-min avg
        self._sad_samples     = []            # samples during baseline window

    # ── Public API ──────────────────────────────────────────────────────
    def update(self, emotions: dict, face_detected: bool) -> tuple[str, dict]:
        """
        Returns (debounced_state, norm_scores_dict [0,1 per state]).
        norm_scores are normalized so all 10 bars sum visually to 1.
        """
        self._window.append(emotions.copy())
        self._update_sad_baseline(emotions)

        scores = {}
        scores.update(self._simple_scores(emotions))
        scores.update(self._time_scores(emotions, face_detected))

        # Normalize to [0, 1] for the bar chart
        total = sum(scores.values()) or 1.0
        norm  = {k: round(v / total, 4) for k, v in scores.items()}

        # Debounce: must win N consecutive cycles to change display
        raw_dom = max(norm, key=norm.get)
        self._debounce_buf.append(raw_dom)
        if len(self._debounce_buf) == self._debounce_buf.maxlen and len(set(self._debounce_buf)) == 1:
            self._state = raw_dom

        self._scores = norm
        return self._state, norm

    def update_external(self, blink_rate=None, head_pose=None, eye_contact=None):
        """Integration hook — MediaPipe will inject signals here."""
        pass

    # ── Layer 1: Simple threshold rules ─────────────────────────────────
    def _simple_scores(self, e: dict) -> dict:
        neutral  = e.get("neutral",  0.0)
        happy    = e.get("happy",    0.0)
        fear     = e.get("fear",     0.0)
        sad      = e.get("sad",      0.0)
        angry    = e.get("angry",    0.0)
        disgust  = e.get("disgust",  0.0)
        surprise = e.get("surprise", 0.0)

        # Calm: neutral dominates (> 85)
        calm = min(1.0, neutral / 85.0) if neutral > 60 else neutral / 150.0

        # Engaged: subtle happy (5-40) OR subtle surprise (5-30), anchored by neutral
        eng_h = 1.0 if 5.0 < happy   < 40.0 else 0.0
        eng_s = 1.0 if 5.0 < surprise < 30.0 else 0.0
        engaged = max(eng_h, eng_s) * max(0.0, neutral / 100.0)

        # Confident: controlled micro-smile — happy > 15 AND neutral > 60
        if happy > 15.0 and neutral > 60.0:
            confident = min(1.0, (happy / 40.0) * (neutral / 80.0))
        else:
            confident = max(0.0, (happy - 15.0) / 100.0)

        # Nervous: fear > 20 OR sad > 20
        n_fear = min(1.0, fear / 50.0) if fear > 20.0 else fear / 120.0
        n_sad  = min(1.0, sad  / 50.0) if sad  > 20.0 else sad  / 120.0
        nervous = max(n_fear, n_sad)

        # Confused: surprise spike + not happy
        if surprise > 30.0 and happy < 5.0:
            confused = min(1.0, surprise / 60.0)
        else:
            confused = surprise / 120.0 * max(0.0, 1.0 - happy / 15.0)

        # Frustrated: anger or disgust elevated
        f_ang  = min(1.0, angry   / 30.0) if angry   > 15.0 else angry   / 120.0
        f_disg = min(1.0, disgust / 20.0) if disgust > 10.0 else disgust / 120.0
        frustrated = max(f_ang, f_disg)

        return {
            "Calm":       calm,
            "Engaged":    engaged,
            "Confident":  confident,
            "Nervous":    nervous,
            "Confused":   confused,
            "Frustrated": frustrated,
        }

    # ── Layer 2: Time-based rules ────────────────────────────────────────
    def _time_scores(self, e: dict, face_detected: bool) -> dict:
        win = list(self._window)

        # ── Thinking: neutral stable ~2s + happy drops ───────────────
        if len(win) >= THINKING_FRAMES:
            recent_n = np.array([w.get("neutral", 0.0) for w in win[-THINKING_FRAMES:]])
            recent_h = np.array([w.get("happy",   0.0) for w in win[-THINKING_FRAMES:]])
            var_n    = float(np.var(recent_n))
            avg_h    = float(np.mean(recent_h))
            # Low variance + happy near zero
            if var_n < 50.0 and avg_h < 10.0:
                thinking = (1.0 - min(1.0, var_n / 50.0)) * (1.0 - min(1.0, avg_h / 10.0))
            else:
                thinking = max(0.0, (1.0 - var_n / 200.0) * 0.25)
        else:
            thinking = 0.0

        # ── Focused: std-dev of neutral < 5 over 5s ─────────────────
        if len(win) >= FOCUSED_FRAMES:
            long_n  = np.array([w.get("neutral", 0.0) for w in win[-FOCUSED_FRAMES:]])
            std_n   = float(np.std(long_n))
            avg_n   = float(np.mean(long_n))
            if std_n < 5.0 and avg_n > 50.0:
                focused = min(1.0, (5.0 - std_n) / 5.0) * (avg_n / 100.0)
            else:
                focused = max(0.0, (5.0 - std_n) / 25.0)
        else:
            focused = 0.0

        # ── Fatigued: sad creeps above baseline by 15% ───────────────
        if self._sad_baseline is not None and len(win) >= FATIGUED_FRAMES:
            recent_sad = np.array([w.get("sad", 0.0) for w in win[-FATIGUED_FRAMES:]])
            avg_sad    = float(np.mean(recent_sad))
            baseline   = self._sad_baseline
            if avg_sad > baseline * 1.15 and baseline > 0:
                fatigued = min(1.0, (avg_sad - baseline) / max(baseline, 1.0))
            else:
                fatigued = min(0.20, e.get("sad", 0.0) / 100.0)
        else:
            fatigued = min(0.20, e.get("sad", 0.0) / 100.0)

        # ── Distracted: face not detected ────────────────────────────
        distracted = 1.0 if not face_detected else 0.0

        return {
            "Thinking":   thinking,
            "Focused":    focused,
            "Fatigued":   fatigued,
            "Distracted": distracted,
        }

    # ── Sad baseline (first 5 minutes of session) ────────────────────────
    def _update_sad_baseline(self, e: dict) -> None:
        if self._sad_baseline is not None:
            return
        elapsed = time.time() - self._session_start
        if elapsed < FATIGUED_BASELINE:
            self._sad_samples.append(e.get("sad", 0.0))
        elif self._sad_samples:
            self._sad_baseline = sum(self._sad_samples) / len(self._sad_samples)
            print(f"[BehavioralClassifier] Sad baseline set: {self._sad_baseline:.1f}%")



class StabilityTracker:
    def __init__(self, window: int = STABILITY_WINDOW):
        self._history = deque(maxlen=window)
        self._state_start = time.time()
        self._last_state = None

    def update(self, state: str) -> tuple[float, float]:
        self._history.append(state)
        if state != self._last_state:
            self._state_start = time.time()
            self._last_state = state
        dur = time.time() - self._state_start
        if len(self._history) < 2: return 1.0, round(dur, 1)
        stability = Counter(self._history).most_common(1)[0][1] / len(self._history)
        return round(stability, 3), round(dur, 1)


class EngagementTracker:
    def __init__(self, window: int = 30):
        self._history = deque([0.80] * window, maxlen=window) # Baseline 80%

    def update(self, state: str, state_score: float) -> float:
        if state in POSITIVE_STATES:
            target = 0.85 + 0.15 * state_score
        elif state in RISK_STATES:
            target = 0.40 + 0.20 * (1.0 - state_score)
        else:
            target = 0.80

        # Smooth EMA transition
        current = self._history[-1]
        val = 0.8 * current + 0.2 * target
        self._history.append(val)
        return round(val, 3)

    def update_external(self, eye_contact=None, head_pose=None, blink_rate=None): pass


class NervousnessTracker:
    def __init__(self, window: int = 20):
        self._history = deque(maxlen=window)

    def update(self, smoothed_probs: dict, stability: float) -> float:
        fear = smoothed_probs.get("fear", 0.0) / 100.0
        disg = smoothed_probs.get("disgust", 0.0) / 100.0
        angr = smoothed_probs.get("angry", 0.0) / 100.0
        raw_affect = 0.55 * fear + 0.30 * disg + 0.15 * angr
        score = 0.65 * raw_affect + 0.35 * (1.0 - stability)
        self._history.append(score)
        return round(sum(self._history) / len(self._history), 3)

    def update_external(self, blink_rate=None, gaze_shifts=None, speech_fillers=None, head_movement=None): pass


class EmotionHistoryLog:
    def __init__(self, seconds: int = HISTORY_SECONDS):
        self._log = deque(maxlen=seconds)
        self._last_tick = time.time()

    def update(self, state: str) -> None:
        if time.time() - self._last_tick >= 1.0:
            self._log.append(state)
            self._last_tick = time.time()

    def timeline(self) -> list[str]: return list(self._log)


class DeepFaceThread:
    def __init__(self):
        self._lock = threading.Lock()
        self._frame, self._result = None, None
        self._running = False
        self._inference_ms, self._last_analysis_t = 0.0, 0.0
        self._fps_times = deque(maxlen=10)
        try: from deepface import DeepFace as _DF; self._DF = _DF
        except ImportError: raise ImportError("Run: pip install deepface tf-keras")

    def start(self):
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self): self._running = False
    def push_frame(self, frame: np.ndarray):
        with self._lock: self._frame = frame.copy()
    
    @property
    def result(self):
        with self._lock: return self._result

    @property
    def inference_ms(self): return self._inference_ms
    @property
    def actual_fps(self):
        ts = list(self._fps_times)
        return (len(ts) - 1) / max(ts[-1] - ts[0], 1e-6) if len(ts) > 1 else 0.0

    def _loop(self):
        while self._running:
            if time.time() - self._last_analysis_t < ANALYSIS_INTERVAL: time.sleep(0.01); continue
            with self._lock: frame = self._frame
            if frame is None: time.sleep(0.02); continue
            try:
                t0 = time.time()
                raw = self._DF.analyze(apply_clahe(frame), actions=["emotion"], detector_backend=DEEPFACE_BACKEND, enforce_detection=False, silent=True)
                self._inference_ms = (time.time() - t0) * 1000
                with self._lock: self._result = raw if isinstance(raw, list) else [raw]
                self._fps_times.append(time.time()); self._last_analysis_t = time.time()
            except Exception: time.sleep(0.1)


# ─────────────────────────────────────────────────────────────────────────────
# Integration Export format
# ─────────────────────────────────────────────────────────────────────────────
def get_standardized_output(data: dict) -> dict:
    """Holistic Interview Engine standard module interface."""
    return {
        "module": "deepface",
        "status": "running" if data.get("analysis_fps", 0) > 0 else "warming_up",
        "quality": data.get("quality", {}).get("score", 0.0),
        "primary_output": {
            "state": data.get("interview_state", "Unknown"),
            "confidence": data.get("state_score", 0.0)
        },
        "secondary_outputs": {
            "raw_emotions": data.get("smoothed_probs", {}),
            "dominant_raw": data.get("dominant_raw", ""),
            "stability": data.get("stability", 0.0),
            "engagement": data.get("engagement", 0.0),
            "nervousness": data.get("nervousness", 0.0)
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# HUD Drawing
# ─────────────────────────────────────────────────────────────────────────────
def _bar(frame, x, y, w, val, color, h=8):
    cv2.rectangle(frame, (x, y-h), (x+w, y), (50,50,50), -1)
    if (f := int(max(0, min(1, val)) * w)) > 0:
        cv2.rectangle(frame, (x, y-h), (x+f, y), color, -1)

def draw_hud(frame, data: dict, fps: float):
    h, w = frame.shape[:2]
    pw = 350
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (pw, h), DARK_PANEL, -1)
    cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

    def put(t, y, c=WHITE, s=0.5, bold=False): cv2.putText(frame, t, (10, y), FONT, s, c, 2 if bold else 1, cv2.LINE_AA)
    def sec(l, y):
        y += 4; cv2.line(frame, (10, y), (pw-10, y), (70,70,70), 1)
        y += 13; cv2.putText(frame, l, (10, y), FONT, 0.38, GRAY, 1, cv2.LINE_AA); return y + 14

    y = 24
    put("EMOTION INTELLIGENCE ENGINE", y, WHITE, 0.50, bold=True); y += 22

    y = sec("CANDIDATE & QUALITY", y)
    locked = data.get("candidate_locked", False)
    put(f"Candidate : {'LOCKED' if locked else 'SEARCHING'}", y, GREEN if locked else YELLOW, 0.42, bold=locked); y += 16

    q = data.get("quality", {}); qs = q.get("score", 0.0)
    qc = GREEN if qs >= 0.70 else YELLOW if qs >= QUALITY_GATE else RED
    sup = data.get("quality_suppressed", False)
    put(f"Quality   : {qs*100:.0f}%{'  [SUPPRESSED]' if sup else ''}", y, qc, 0.42, bold=sup); y += 14
    put(f"Lighting: {q.get('lighting','-')}   Blur: {q.get('blur_label','-')}", y, GRAY, 0.38); y += 14

    y = sec("FACIAL EMOTIONAL STATE", y)
    state = data.get("interview_state", "Initializing...")
    state_s = data.get("state_score", 0.0)
    dur = data.get("state_duration", 0.0)
    sc = STATE_COLORS.get(state, WHITE)
    put(f"{state}  ({state_s*100:.0f}%)", y, sc, 0.65, bold=True); y += 22
    put(f"{state} for {dur:.1f} seconds", y, GRAY, 0.42); y += 16

    # ── Raw 7 Emotions ───────────────────────────────────────────────────
    y = sec("RAW EMOTION SCORES", y)
    RAW_ORDER = [
        ("Angry", "angry"),
        ("Disgust", "disgust"),
        ("Fear", "fear"),
        ("Happiness", "happy"),
        ("Sadness", "sad"),
        ("Surprise", "surprise"),
        ("Neutral", "neutral")
    ]
    raw_probs = data.get("smoothed_probs", {})
    for lbl, key in RAW_ORDER:
        v = raw_probs.get(key, 0.0)
        c = GRAY if key == "neutral" else (ORANGE if key in ("angry","disgust","fear","sad") else GREEN)
        put(lbl, y, GRAY, 0.38)
        _bar(frame, 90, y, 200, v / 100.0, c)
        cv2.putText(frame, f"{v:.1f}%", (300, y), FONT, 0.36, GRAY, 1, cv2.LINE_AA)
        y += 14
    
    cv2.line(frame, (0, h - 22), (pw, h - 22), (60, 60, 60), 1)
    put("q = quit   r = reset lock", h - 7, GRAY, 0.38)


def draw_candidate_box(frame, region, locked):
    x, y, w, h = region.get("x",0), region.get("y",0), region.get("w",0), region.get("h",0)
    x2, y2 = x + w, y + h
    c = GREEN if locked else YELLOW
    for (px, py, dx, dy) in [(x, y, 1, 1), (x2, y, -1, 1), (x, y2, 1, -1), (x2, y2, -1, -1)]:
        cv2.line(frame, (px, py), (px + dx * 18, py), c, 2)
        cv2.line(frame, (px, py), (px, py + dy * 18), c, 2)
    cv2.putText(frame, "CANDIDATE" if locked else "SEARCHING", (x, y - 6), FONT, 0.45, c, 1, cv2.LINE_AA)


def main():
    cap = open_camera()
    if not cap: return

    df_thread = DeepFaceThread()
    smoother = TemporalSmoother(alpha=EMA_ALPHA)
    tracker = CandidateTracker()
    interpreter = BehavioralStateClassifier(debounce=DEBOUNCE_CYCLES)
    quality_assr = EmotionQualityAssessor()
    stability_trk = StabilityTracker(window=STABILITY_WINDOW)
    engagement_trk = EngagementTracker(window=30)
    nervousness_trk = NervousnessTracker(window=20)
    history_log = EmotionHistoryLog(seconds=HISTORY_SECONDS)

    df_thread.start()

    fps_hist = deque(maxlen=30)
    last_time = time.perf_counter()
    hud_data = {}

    while True:
        ret, frame = cap.read()
        if not ret: break

        now = time.perf_counter()
        fps_hist.append(1.0 / (now - last_time if now > last_time else 1e-6))
        last_time = now

        df_thread.push_frame(frame)
        res = df_thread.result
        fh, fw = frame.shape[:2]

        if res:
            regions = [r.get("region", {}) for r in res]
            face_count = len([r for r in regions if r.get("w", 0) > 10])
            cand = tracker.select(regions, fw, fh)

            if cand:
                c_res = next((r for r in res if r.get("region", {}) == cand), res[0])
                raw_probs = c_res.get("emotion", {})
                smoothed = smoother.update(raw_probs)
                
                q_data = quality_assr.assess(frame, cand, fw, fh)
                suppressed = q_data["score"] < QUALITY_GATE

                if not suppressed:
                    state, norm = interpreter.update(smoothed, face_detected=True)
                    state_s = norm.get(state, 0.0)
                    r_dom = max(smoothed, key=smoothed.get) if smoothed else "neutral"
                    r_val = smoothed.get(r_dom, 0.0)
                    stab, dur = stability_trk.update(state)
                    eng = engagement_trk.update(state, state_s)
                    nerv = nervousness_trk.update(smoothed, stab)
                    history_log.update(state)
                else:
                    state = hud_data.get("interview_state", "Low Quality")
                    state_s = hud_data.get("state_score", 0.0)
                    stab, dur = stability_trk.update(state)
                    eng = hud_data.get("engagement", 0.0)
                    nerv = hud_data.get("nervousness", 0.0)
                    r_dom, r_val = hud_data.get("dominant_raw", ""), hud_data.get("dominant_raw_val", 0.0)

                draw_candidate_box(frame, cand, tracker.is_locked)
                hud_data.update({
                    "face_count": face_count, "candidate_locked": tracker.is_locked,
                    "interview_state": state, "state_score": state_s, "state_duration": dur,
                    "engagement": eng, "stability": stab, "nervousness": nerv,
                    "smoothed_probs": smoothed, "dominant_raw": r_dom, "dominant_raw_val": r_val,
                    "norm_scores": norm if not suppressed else hud_data.get("norm_scores", {}),
                    "quality": q_data, "quality_suppressed": suppressed,
                    "history_timeline": history_log.timeline(),
                    "analysis_fps": df_thread.actual_fps, "inference_ms": df_thread.inference_ms,
                })
            else:
                hud_data.update({"face_count": face_count, "candidate_locked": tracker.is_locked, "interview_state": "Detecting..."})
        else:
            hud_data["interview_state"] = "Warming up..."

        draw_hud(frame, hud_data, sum(fps_hist)/len(fps_hist))
        cv2.imshow("DeepFace Emotion Intelligence Engine", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'): break
        elif cv2.waitKey(1) & 0xFF == ord('r'): tracker.force_reset()

    df_thread.stop(); cap.release(); cv2.destroyAllWindows()
    
    print("\nHolistic Interface Output (JSON):")
    import json
    print(json.dumps(get_standardized_output(hud_data), indent=2))

if __name__ == "__main__": main()
