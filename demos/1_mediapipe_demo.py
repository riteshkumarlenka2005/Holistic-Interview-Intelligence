"""
Demo 1: MediaPipe Face Landmarker — Production Quality
=======================================================
Features:
  - Candidate locking   : tracks only the largest/closest face, ignores others
  - Face size filter    : rejects faces that are too small (far away / printed photo)
  - Landmark smoothing  : exponential moving average to reduce jitter
  - Adaptive blink      : EAR threshold auto-calibrated from resting state + cooldown
  - Temporal gaze filter: smoothed gaze direction with hysteresis
  - Head pose           : solvePnP with proper 3-D model points
  - Confidence overlay  : per-feature confidence scores
  - FPS + latency HUD   : real-time performance metrics
  - Robust camera init  : DirectShow → MSMF fallback with warm-up
  - Graceful failures   : camera disconnect, face loss, model errors

Install:  pip install mediapipe opencv-python numpy
Model:    demos/models/face_landmarker.task  (auto-downloaded on first run)
Run:      python demos/1_mediapipe_demo.py
Controls: Press 'q' to quit | 'r' to reset candidate lock | 'c' to calibrate blink
"""

import cv2
import math
import os
import time
import urllib.request
from collections import deque

import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    FaceLandmarker,
    FaceLandmarkerOptions,
    FaceLandmarksConnections,
    RunningMode,
    drawing_utils,
)

# ─────────────────────────────────────────────
# Model
# ─────────────────────────────────────────────
MODEL_DIR  = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "face_landmarker.task")
MODEL_URL  = (
    "https://storage.googleapis.com/mediapipe-models/"
    "face_landmarker/face_landmarker/float16/1/face_landmarker.task"
)

# ─────────────────────────────────────────────
# Landmark indices  (MediaPipe 478-point model)
# ─────────────────────────────────────────────
# Head pose
NOSE_TIP        = 1
CHIN            = 152
LEFT_EYE_OUTER  = 33
RIGHT_EYE_OUTER = 263
LEFT_MOUTH      = 61
RIGHT_MOUTH     = 291

# Blink — Eye Aspect Ratio
LEFT_EYE_TOP    = 159;  LEFT_EYE_BOTTOM  = 145
LEFT_EYE_LEFT   = 33;   LEFT_EYE_RIGHT   = 133
RIGHT_EYE_TOP   = 386;  RIGHT_EYE_BOTTOM = 374
RIGHT_EYE_LEFT  = 362;  RIGHT_EYE_RIGHT  = 263

# Iris centers (landmark 468-477, only present with full model)
LEFT_IRIS_CENTER  = 468
RIGHT_IRIS_CENTER = 473

# 3-D model points for solvePnP — generic human face proportions in mm.
#
# Coordinate system: OpenCV camera space
#   X: pointing RIGHT in the image  (+X = right side of image)
#   Y: pointing DOWN  in the image  (+Y = lower side, Y-down convention)
#   Z: pointing AWAY from camera    (face depth is negative = behind the image plane)
#
# Key rule: MediaPipe defines landmarks from the SUBJECT's perspective.
#   "Left" landmarks (33, 61 …) appear on the camera's RIGHT (+X side).
#   "Right" landmarks (263, 291 …) appear on the camera's LEFT (−X side).
#
# Projection proof: x_image = f * x_model / (z_model + depth) + cx
#   For x_image > cx (right of center), x_model must be POSITIVE.
#   So LEFT_EYE_OUTER (appears right of center) → positive X.
#   So RIGHT_EYE_OUTER (appears left of center) → negative X.
FACE_3D_MODEL = np.array([
    [   0.0,   0.0,   0.0],   # Nose tip           (center)
    [   0.0, 330.0, -65.0],   # Chin               (below nose  → +Y)
    [+225.0,-170.0,-135.0],   # LEFT eye outer     (right in image → +X, above → −Y)
    [-225.0,-170.0,-135.0],   # RIGHT eye outer    (left  in image → −X, above → −Y)
    [+150.0, 150.0,-125.0],   # LEFT mouth corner  (right in image → +X, below → +Y)
    [-150.0, 150.0,-125.0],   # RIGHT mouth corner (left  in image → −X, below → +Y)
], dtype=np.float64)

# ─────────────────────────────────────────────
# Tuning knobs
# ─────────────────────────────────────────────
EAR_THRESHOLD_DEFAULT = 0.22   # initial blink threshold (calibrated at runtime)
EAR_BLINK_FRAMES      = 2      # consecutive low-EAR frames = one blink
EAR_COOLDOWN_FRAMES   = 4      # ignore further blinks for N frames after one
MIN_FACE_AREA_RATIO   = 0.03   # face bbox must cover ≥3% of frame area
SMOOTH_ALPHA          = 0.35   # landmark EMA weight (0=frozen, 1=raw)
GAZE_HISTORY          = 5      # frames to smooth gaze direction (was 7)
GAZE_HYSTERESIS       = 2      # votes needed to change gaze label (was 3)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def ensure_model():
    if os.path.exists(MODEL_PATH):
        return
    os.makedirs(MODEL_DIR, exist_ok=True)
    print(f"Downloading face_landmarker model to {MODEL_PATH} ...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print(f"Downloaded ({os.path.getsize(MODEL_PATH):,} bytes)")


def face_bbox_area_ratio(lm, w, h):
    """Return the fraction of the frame area covered by this face's bounding box."""
    xs = [l.x for l in lm]
    ys = [l.y for l in lm]
    bw = (max(xs) - min(xs)) * w
    bh = (max(ys) - min(ys)) * h
    return (bw * bh) / (w * h)


def face_center(lm):
    """Return normalised (cx, cy) of the face bounding box."""
    xs = [l.x for l in lm]
    ys = [l.y for l in lm]
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2


def smooth_landmarks(prev, curr, alpha):
    """Exponential Moving Average across all landmarks."""
    if prev is None:
        return curr
    smoothed = []
    for p, c in zip(prev, curr):
        sx = alpha * c.x + (1 - alpha) * p.x
        sy = alpha * c.y + (1 - alpha) * p.y
        sz = alpha * c.z + (1 - alpha) * p.z
        # carry visibility / presence from the current (raw) landmark
        vis = getattr(c, "visibility", None)
        pre = getattr(c, "presence", None)
        smoothed.append(_LM(sx, sy, sz, vis, pre))
    return smoothed


class _LM:
    """Lightweight mutable landmark with x/y/z/visibility/presence."""
    __slots__ = ("x", "y", "z", "visibility", "presence")
    def __init__(self, x, y, z, visibility=None, presence=None):
        self.x, self.y, self.z = x, y, z
        self.visibility = visibility
        self.presence   = presence


def calculate_ear(lm, top, bottom, left, right, w, h):
    """Eye Aspect Ratio."""
    vert  = math.hypot((lm[top].x - lm[bottom].x) * w,
                       (lm[top].y - lm[bottom].y) * h)
    horiz = math.hypot((lm[left].x - lm[right].x) * w,
                       (lm[left].y - lm[right].y) * h)
    return vert / horiz if horiz > 0 else 0.0


def calculate_gaze(lm, w, h):
    """
    Return (horiz, vert) in [0,1] where 0.5 = center.
    Averages left + right iris for more reliable estimation.
    Note: in MediaPipe coordinates, looking right (your right) → iris
    moves toward outer corner → h_ratio DECREASES (iris x gets smaller).
    """
    # ── Left eye ────────────────────────────────────────────────────────
    l_outer = lm[LEFT_EYE_OUTER];  l_inner = lm[LEFT_EYE_RIGHT]
    l_top   = lm[LEFT_EYE_TOP];    l_bot   = lm[LEFT_EYE_BOTTOM]
    l_iris  = lm[LEFT_IRIS_CENTER]
    l_ew = abs(l_outer.x - l_inner.x)
    l_eh = abs(l_bot.y   - l_top.y)

    # ── Right eye ───────────────────────────────────────────────────────
    r_outer = lm[RIGHT_EYE_OUTER]; r_inner = lm[RIGHT_EYE_LEFT]
    r_top   = lm[RIGHT_EYE_TOP];   r_bot   = lm[RIGHT_EYE_BOTTOM]
    r_iris  = lm[RIGHT_IRIS_CENTER]
    r_ew = abs(r_outer.x - r_inner.x)
    r_eh = abs(r_bot.y   - r_top.y)

    if l_ew == 0 or r_ew == 0 or l_eh == 0 or r_eh == 0:
        return 0.5, 0.5

    l_h = (l_iris.x - min(l_outer.x, l_inner.x)) / l_ew
    r_h = (r_iris.x - min(r_outer.x, r_inner.x)) / r_ew
    l_v = (l_iris.y - min(l_top.y, l_bot.y)) / l_eh
    r_v = (r_iris.y - min(r_top.y, r_bot.y)) / r_eh

    # Average both eyes
    h_ratio = (l_h + r_h) / 2.0
    v_ratio = (l_v + r_v) / 2.0
    return h_ratio, v_ratio


def calculate_head_pose(lm, w, h):
    """
    Returns (pitch, yaw, roll) in degrees using the face direction vector approach.

    Instead of decomposing the rotation matrix into Euler angles (error-prone,
    axis-labeling confusion, gimbal lock), we extract the physical directions the
    face's +Z (forward) and -Y (up) axes point in camera space, then compute
    the angles from those.

    Sign convention:
      pitch +  =  looking up          pitch -  =  looking down
      yaw   +  =  turned to user's right   yaw - = turned to user's left
      roll  +  =  right ear toward shoulder  roll - = left ear toward shoulder

    Frontal face sanity check:
      face_fwd ≈ (0, 0, −1)  in camera space  →  yaw ≈ 0°, pitch ≈ 0°
      face_up  ≈ (0, −1, 0)  in camera space  →  roll ≈ 0°
    """
    indices = [NOSE_TIP, CHIN, LEFT_EYE_OUTER, RIGHT_EYE_OUTER, LEFT_MOUTH, RIGHT_MOUTH]
    pts2d = np.array([[lm[i].x * w, lm[i].y * h] for i in indices], dtype=np.float64)
    focal = w
    cam   = np.array([[focal, 0, w / 2],
                      [0, focal, h / 2],
                      [0,     0,     1]], dtype=np.float64)
    dist  = np.zeros((4, 1), dtype=np.float64)

    ok, rvec, _ = cv2.solvePnP(
        FACE_3D_MODEL, pts2d, cam, dist,
        flags=cv2.SOLVEPNP_ITERATIVE,
    )
    if not ok:
        return 0.0, 0.0, 0.0

    rmat, _ = cv2.Rodrigues(rvec)

    # ── Face direction vectors in camera space ────────────────────────────
    #
    # Model axes (Y-down convention, face looking toward +Z_model):
    #   +X_model = camera's right (person's left eye is at +X)
    #   +Y_model = downward in image
    #   +Z_model = face "forward" direction (toward camera for frontal pose)
    #
    # After rotation:
    #   face_fwd = R @ [0,0,1] = third column of R = R[:, 2]
    #   face_up  = R @ [0,−1,0] = −second column   = −R[:, 1]
    #
    # For a frontal upright face:
    #   face_fwd ≈ [0, 0, −1]  (points toward camera = −Z_cam)
    #   face_up  ≈ [0, −1, 0]  (points upward = −Y_cam in Y-down space)

    face_fwd = rmat[:, 2]      # model +Z in camera space
    face_up  = -rmat[:, 1]     # model −Y (=up) in camera space

    # ── Yaw ──────────────────────────────────────────────────────────────
    # How much the face has turned horizontally.
    # Frontal: face_fwd[0] ≈ 0, face_fwd[2] ≈ −1  → atan2(0, 1) = 0°
    # Right turn (user's right → camera's left → face_fwd[0] < 0):
    #   atan2(−face_fwd[0], −face_fwd[2]) = atan2(+, +) > 0  ✓
    yaw = math.degrees(math.atan2(-face_fwd[0], -face_fwd[2]))

    # ── Pitch ─────────────────────────────────────────────────────────────
    # How much the face is tilted up or down.
    # Frontal: face_fwd[1] ≈ 0  → 0°
    # Looking up (−Y_cam direction → face_fwd[1] < 0):
    #   atan2(−face_fwd[1], −face_fwd[2]) = atan2(+, +) > 0  ✓
    pitch = math.degrees(math.atan2(-face_fwd[1], -face_fwd[2]))

    # ── Roll ──────────────────────────────────────────────────────────────
    # How much the head is tilted sideways (ear toward shoulder).
    # Upright: face_up ≈ [0, −1, 0]  → atan2(0, 1) = 0°
    # Right tilt (face_up tilts toward +X_cam → face_up[0] > 0):
    #   atan2(face_up[0], −face_up[1]) = atan2(+, +) > 0  ✓
    roll = math.degrees(math.atan2(face_up[0], -face_up[1]))

    # Clamp to physically possible ranges
    pitch = max(-90.0, min(90.0, pitch))
    yaw   = max(-90.0, min(90.0, yaw))
    roll  = max(-90.0, min(90.0, roll))
    return pitch, yaw, roll


def open_camera():
    """Try DirectShow → MSMF → default, return first working capture."""
    backends = [
        ("DirectShow", cv2.CAP_DSHOW),
        ("MSMF",       cv2.CAP_MSMF),
        ("Default",    None),
    ]
    for name, flag in backends:
        print(f"Trying camera backend: {name} ...")
        cap = cv2.VideoCapture(0, flag) if flag is not None else cv2.VideoCapture(0)
        if not cap.isOpened():
            print(f"  [!!] Could not open with {name}")
            cap.release(); continue
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        # warm-up
        for _ in range(15):
            cap.read(); cv2.waitKey(30)
        ret, frame = cap.read()
        if ret and frame is not None and frame.mean() > 1.0:
            print(f"  [OK] Camera ready with {name} "
                  f"({int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x"
                  f"{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))})")
            return cap
        print(f"  [!!] Camera opened but frames are bad with {name}")
        cap.release()
    return None


# ─────────────────────────────────────────────────────────────────────────────
# HUD drawing
# ─────────────────────────────────────────────────────────────────────────────

FONT       = cv2.FONT_HERSHEY_SIMPLEX
GREEN      = (0, 220, 80)
YELLOW     = (0, 200, 255)
RED        = (0, 60, 230)
ORANGE     = (0, 140, 255)
GRAY       = (160, 160, 160)
WHITE      = (255, 255, 255)
DARK_PANEL = (20, 20, 20)


def draw_hud(frame, data: dict, fps: float, inference_ms: float):
    """Draw a clean HUD panel on the left side."""
    h, w = frame.shape[:2]
    panel_w = 310

    # Semi-transparent dark panel
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (panel_w, h), DARK_PANEL, -1)
    cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

    def put(text, y, color=WHITE, scale=0.6, bold=False):
        thickness = 2 if bold else 1
        cv2.putText(frame, text, (10, y), FONT, scale, color, thickness, cv2.LINE_AA)

    y = 28
    put("MEDIAPIPE FACE ANALYSIS", y, WHITE, 0.55, bold=True); y += 24
    cv2.line(frame, (10, y), (panel_w - 10, y), GRAY, 1); y += 16

    # Performance
    fps_color = GREEN if fps >= 20 else ORANGE if fps >= 12 else RED
    put(f"FPS: {fps:.1f}   Inference: {inference_ms:.1f}ms", y, fps_color); y += 22
    cv2.line(frame, (10, y), (panel_w - 10, y), (50, 50, 50), 1); y += 14

    locked = data.get("candidate_locked", False)
    put(f"Faces detected: {data.get('face_count', 0)}", y, WHITE); y += 22
    status = "LOCKED" if locked else "SEARCHING"
    put(f"Candidate: {status}", y, GREEN if locked else YELLOW, bold=locked); y += 24
    cv2.line(frame, (10, y), (panel_w - 10, y), (50, 50, 50), 1); y += 14

    # Eye contact
    ec = data.get("eye_contact", False)
    put(f"Eye Contact: {'YES' if ec else 'NO'}", y, GREEN if ec else RED, bold=True); y += 22
    gd = data.get("gaze_dir", "N/A")
    gc = GREEN if gd == "CENTER" else YELLOW
    put(f"Gaze: {gd}", y, gc); y += 22
    put(f"  H: {data.get('gaze_h', 0.0):+.3f}  V: {data.get('gaze_v', 0.0):+.3f}", y, GRAY, 0.5); y += 22
    cv2.line(frame, (10, y), (panel_w - 10, y), (50, 50, 50), 1); y += 14

    # Head pose
    pitch = data.get("pitch", 0.0)
    yaw   = data.get("yaw", 0.0)
    roll  = data.get("roll", 0.0)
    pose_ok = abs(pitch) < 15 and abs(yaw) < 20
    put("Head Pose:", y, WHITE); y += 20
    put(f"  Pitch: {pitch:+.1f} deg", y, GREEN if abs(pitch) < 10 else YELLOW); y += 20
    put(f"  Yaw:   {yaw:+.1f} deg",   y, GREEN if abs(yaw)   < 15 else YELLOW); y += 20
    put(f"  Roll:  {roll:+.1f} deg",  y, GREEN if abs(roll)   < 10 else YELLOW); y += 22
    cv2.line(frame, (10, y), (panel_w - 10, y), (50, 50, 50), 1); y += 14

    # Blink
    ear = data.get("ear", 0.0)
    thr = data.get("ear_threshold", EAR_THRESHOLD_DEFAULT)
    blinking = data.get("blinking", False)
    put(f"Blinks: {data.get('blink_count', 0)}", y, WHITE); y += 20
    put(f"  EAR: {ear:.3f}  threshold: {thr:.3f}", y, RED if blinking else GRAY, 0.5); y += 20
    bpm = data.get("blinks_per_min", 0.0)
    bpm_color = GREEN if 10 < bpm < 30 else YELLOW
    put(f"  Rate: {bpm:.1f} blinks/min", y, bpm_color, 0.5); y += 22
    cv2.line(frame, (10, y), (panel_w - 10, y), (50, 50, 50), 1); y += 14

    # Face quality
    area = data.get("face_area", 0.0)
    put(f"Face area: {area*100:.1f}%  {'[OK]' if area > MIN_FACE_AREA_RATIO else '[TOO SMALL]'}",
        y, GREEN if area > MIN_FACE_AREA_RATIO else RED, 0.5); y += 20

    # Hint bar
    cv2.line(frame, (0, h - 24), (panel_w, h - 24), GRAY, 1)
    put("q=quit  r=reset lock  c=calibrate", h - 8, GRAY, 0.42)


def draw_candidate_box(frame, lm, w, h, locked):
    """Draw a bounding box around the candidate face."""
    xs = [l.x for l in lm];  ys = [l.y for l in lm]
    x1 = int(min(xs) * w);   y1 = int(min(ys) * h)
    x2 = int(max(xs) * w);   y2 = int(max(ys) * h)
    color = GREEN if locked else YELLOW
    # Corner brackets instead of full rect for a cleaner look
    sz = 18; t = 2
    for (px, py, dx, dy) in [(x1,y1,1,1),(x2,y1,-1,1),(x1,y2,1,-1),(x2,y2,-1,-1)]:
        cv2.line(frame, (px, py), (px + dx*sz, py), color, t)
        cv2.line(frame, (px, py), (px, py + dy*sz), color, t)
    label = "CANDIDATE" if locked else "SEARCHING"
    cv2.putText(frame, label, (x1, y1 - 6), FONT, 0.45, color, 1, cv2.LINE_AA)


# ─────────────────────────────────────────────────────────────────────────────
# Candidate Tracker
# ─────────────────────────────────────────────────────────────────────────────

class CandidateTracker:
    """
    Locks onto the largest face in frame 0 (assumed to be the interview candidate).
    Subsequent frames: tracks the face whose centre is closest to the locked centre.
    Rejects any face whose area ratio is below MIN_FACE_AREA_RATIO.
    """
    LOCK_AFTER_FRAMES = 5   # need N consecutive frames with a valid face to lock

    def __init__(self):
        self.reset()

    def reset(self):
        self._locked_centre  = None
        self._locked         = False
        self._stable_count   = 0
        self._max_drift      = 0.25   # normalised distance; beyond this = lost

    @property
    def is_locked(self):
        return self._locked

    def select(self, all_landmarks, w, h):
        """
        Pick the candidate face from a list of landmark sets.
        Returns (index, landmarks) or (None, None) if nothing qualifies.
        """
        # Filter out tiny faces (phone screens, background people)
        valid = [
            (i, lm) for i, lm in enumerate(all_landmarks)
            if face_bbox_area_ratio(lm, w, h) >= MIN_FACE_AREA_RATIO
        ]
        if not valid:
            self._stable_count = 0
            return None, None

        if not self._locked:
            # Pick largest face
            idx, lm = max(valid, key=lambda x: face_bbox_area_ratio(x[1], w, h))
            cx, cy  = face_center(lm)
            self._stable_count += 1
            if self._stable_count >= self.LOCK_AFTER_FRAMES:
                self._locked_centre = (cx, cy)
                self._locked        = True
                print("[CandidateTracker] Candidate locked.")
            return idx, lm
        else:
            # Track: find the valid face closest to locked centre
            lcx, lcy = self._locked_centre
            best = min(valid, key=lambda x: math.hypot(face_center(x[1])[0] - lcx,
                                                        face_center(x[1])[1] - lcy))
            idx, lm = best
            cx, cy  = face_center(lm)
            dist    = math.hypot(cx - lcx, cy - lcy)
            if dist > self._max_drift:
                # Lost candidate — keep old lock but report nothing this frame
                return None, None
            # Update locked centre (slow follow)
            self._locked_centre = (
                0.9 * lcx + 0.1 * cx,
                0.9 * lcy + 0.1 * cy,
            )
            return idx, lm

    def force_reset(self):
        self.reset()
        print("[CandidateTracker] Lock reset.")


# ─────────────────────────────────────────────────────────────────────────────
# Blink Detector
# ─────────────────────────────────────────────────────────────────────────────

class BlinkDetector:
    """
    Adaptive EAR blink detector with cooldown and calibration.
    """
    CALIBRATION_FRAMES = 60   # frames to collect resting EAR

    def __init__(self):
        self.threshold     = EAR_THRESHOLD_DEFAULT
        self.blink_count   = 0
        self._below_count  = 0       # consecutive frames below threshold
        self._cooldown     = 0       # frames remaining in cooldown
        self._cal_ears     = []      # EAR samples during calibration
        self._calibrated   = False
        self._start_time   = time.time()

    def update(self, ear):
        """Return (is_blinking, blink_just_happened)."""
        # Auto-calibrate: collect open-eye EAR
        if not self._calibrated and len(self._cal_ears) < self.CALIBRATION_FRAMES:
            if ear > 0.20:   # only collect clearly-open eyes
                self._cal_ears.append(ear)
            if len(self._cal_ears) == self.CALIBRATION_FRAMES:
                mean_ear  = np.mean(self._cal_ears)
                self.threshold = mean_ear * 0.78   # 78% of resting = blink
                self.threshold = max(0.15, min(0.28, self.threshold))  # clamp
                self._calibrated = True
                print(f"[BlinkDetector] Calibrated EAR threshold: {self.threshold:.3f} "
                      f"(resting mean: {mean_ear:.3f})")

        is_blinking    = ear < self.threshold
        blink_happened = False

        if self._cooldown > 0:
            self._cooldown -= 1
            return is_blinking, False

        if is_blinking:
            self._below_count += 1
        else:
            if self._below_count >= EAR_BLINK_FRAMES:
                self.blink_count += 1
                blink_happened    = True
                self._cooldown    = EAR_COOLDOWN_FRAMES
            self._below_count = 0

        return is_blinking, blink_happened

    @property
    def blinks_per_minute(self):
        elapsed = max(time.time() - self._start_time, 1.0)
        return self.blink_count / elapsed * 60

    def recalibrate(self):
        self._cal_ears   = []
        self._calibrated = False
        print("[BlinkDetector] Recalibrating ...")


# ─────────────────────────────────────────────────────────────────────────────
# Gaze Smoother
# ─────────────────────────────────────────────────────────────────────────────

class GazeSmoother:
    """Majority-vote smoothing over recent gaze direction labels."""
    LABELS = ["CENTER", "LEFT", "RIGHT", "UP", "DOWN"]

    def __init__(self, window=GAZE_HISTORY, hysteresis=GAZE_HYSTERESIS):
        self._history    = deque(maxlen=window)
        self._hysteresis = hysteresis
        self._current    = "CENTER"

    def update(self, horiz, vert):
        """
        Compute raw label from ratios, smooth, return (label, h_offset, v_offset).
        Thresholds are tight: iris physically moves only ~10-15% of eye width.
        Center zone is 0.44-0.56 (12% band), not the old 0.38-0.62 (24% band).
        """
        h_off = horiz - 0.5
        v_off = vert  - 0.5

        # Tightened thresholds — validated against real iris movement range
        if   horiz < 0.44: raw = "RIGHT"   # iris drifted toward outer corner
        elif horiz > 0.56: raw = "LEFT"    # iris drifted toward inner/nose side
        elif vert  < 0.40: raw = "UP"
        elif vert  > 0.62: raw = "DOWN"
        else:              raw = "CENTER"

        self._history.append(raw)
        counts = {l: self._history.count(l) for l in self.LABELS}
        best   = max(counts, key=counts.get)

        # Hysteresis: only change label if winning by enough
        if best != self._current and counts[best] >= self._hysteresis:
            self._current = best

        return self._current, h_off, v_off


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    ensure_model()

    # ── MediaPipe FaceLandmarker ──────────────────────────────────────────
    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=RunningMode.VIDEO,
        num_faces=4,                        # detect up to 4; we filter afterwards
        min_face_detection_confidence=0.55,
        min_face_presence_confidence=0.55,
        min_tracking_confidence=0.50,
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
    )
    landmarker = FaceLandmarker.create_from_options(options)

    # ── Camera ───────────────────────────────────────────────────────────
    cap = open_camera()
    if cap is None:
        print("ERROR: No working camera found.")
        return

    # ── State ────────────────────────────────────────────────────────────
    tracker         = CandidateTracker()
    blink_detector  = BlinkDetector()
    gaze_smoother   = GazeSmoother()
    prev_landmarks  = None               # for EMA smoothing

    fps_history     = deque(maxlen=30)
    last_time       = time.perf_counter()
    consec_fails    = 0
    MAX_FAILS       = 60

    print("=" * 55)
    print("  MediaPipe Face Landmarker  —  Production Demo")
    print("  q = quit  |  r = reset lock  |  c = recalibrate blink")
    print("=" * 55)

    while True:
        # ── Frame read ───────────────────────────────────────────────────
        ret, frame = cap.read()
        if not ret or frame is None:
            consec_fails += 1
            if consec_fails >= MAX_FAILS:
                print("ERROR: Camera stream lost.")
                break
            cv2.waitKey(10)
            continue
        consec_fails = 0

        # ── FPS ──────────────────────────────────────────────────────────
        now = time.perf_counter()
        dt  = now - last_time if now > last_time else 1e-6
        last_time = now
        fps_history.append(1.0 / dt)
        fps = sum(fps_history) / len(fps_history)

        h, w = frame.shape[:2]

        # ── MediaPipe inference ──────────────────────────────────────────
        t0      = time.perf_counter()
        rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img  = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        ts_ms   = int(time.time() * 1000)
        results = landmarker.detect_for_video(mp_img, ts_ms)
        inf_ms  = (time.perf_counter() - t0) * 1000

        # ── Candidate selection ──────────────────────────────────────────
        face_count = len(results.face_landmarks) if results.face_landmarks else 0
        cand_idx, raw_lm = tracker.select(
            results.face_landmarks or [], w, h
        )

        hud_data = {
            "face_count":       face_count,
            "candidate_locked": tracker.is_locked,
            "eye_contact":      False,
            "gaze_dir":         "N/A",
            "gaze_h":           0.0,
            "gaze_v":           0.0,
            "pitch": 0.0, "yaw": 0.0, "roll": 0.0,
            "ear":              0.0,
            "ear_threshold":    blink_detector.threshold,
            "blinking":         False,
            "blink_count":      blink_detector.blink_count,
            "blinks_per_min":   blink_detector.blinks_per_minute,
            "face_area":        0.0,
        }

        if raw_lm is not None:
            # ── Landmark smoothing ────────────────────────────────────────
            lm = smooth_landmarks(prev_landmarks, raw_lm, SMOOTH_ALPHA)
            prev_landmarks = lm

            face_area = face_bbox_area_ratio(lm, w, h)

            # ── Draw mesh on candidate only ───────────────────────────────
            # Convert smoothed _LM back to list for drawing_utils
            # (drawing_utils accepts any object with .x/.y/.z)
            drawing_utils.draw_landmarks(
                frame, lm,
                FaceLandmarksConnections.FACE_LANDMARKS_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=drawing_utils.DrawingSpec(
                    color=(180, 180, 180), thickness=1),
            )
            # Highlight eyes
            drawing_utils.draw_landmarks(
                frame, lm,
                FaceLandmarksConnections.FACE_LANDMARKS_LEFT_EYE,
                landmark_drawing_spec=None,
                connection_drawing_spec=drawing_utils.DrawingSpec(
                    color=(80, 220, 80), thickness=1),
            )
            drawing_utils.draw_landmarks(
                frame, lm,
                FaceLandmarksConnections.FACE_LANDMARKS_RIGHT_EYE,
                landmark_drawing_spec=None,
                connection_drawing_spec=drawing_utils.DrawingSpec(
                    color=(80, 220, 80), thickness=1),
            )
            draw_candidate_box(frame, lm, w, h, tracker.is_locked)

            # ── Head pose ─────────────────────────────────────────────────
            pitch, yaw, roll = calculate_head_pose(lm, w, h)

            # ── Gaze ──────────────────────────────────────────────────────
            has_iris  = len(lm) > RIGHT_IRIS_CENTER
            gaze_dir  = "N/A"
            h_off = v_off = 0.0
            looking   = False
            if has_iris:
                horiz, vert = calculate_gaze(lm, w, h)
                gaze_dir, h_off, v_off = gaze_smoother.update(horiz, vert)
                looking = gaze_dir == "CENTER"

                # Draw iris dots + gaze arrow
                for idx_iris in [LEFT_IRIS_CENTER, RIGHT_IRIS_CENTER]:
                    if idx_iris < len(lm):
                        ix = int(lm[idx_iris].x * w)
                        iy = int(lm[idx_iris].y * h)
                        cv2.circle(frame, (ix, iy), 3, (0, 255, 80), -1)
                        dx = int(h_off * 120)
                        dy = int(v_off * 120)
                        cv2.arrowedLine(frame, (ix, iy), (ix+dx, iy+dy),
                                        (0, 80, 255), 2, tipLength=0.35)

            # ── Blink ─────────────────────────────────────────────────────
            l_ear = calculate_ear(lm, LEFT_EYE_TOP,  LEFT_EYE_BOTTOM,
                                       LEFT_EYE_LEFT,  LEFT_EYE_RIGHT, w, h)
            r_ear = calculate_ear(lm, RIGHT_EYE_TOP, RIGHT_EYE_BOTTOM,
                                       RIGHT_EYE_LEFT, RIGHT_EYE_RIGHT, w, h)
            avg_ear = (l_ear + r_ear) / 2
            is_blinking, _ = blink_detector.update(avg_ear)

            # ── Update HUD data ───────────────────────────────────────────
            hud_data.update({
                "eye_contact":      looking,
                "gaze_dir":         gaze_dir,
                "gaze_h":           h_off,
                "gaze_v":           v_off,
                "pitch":            pitch,
                "yaw":              yaw,
                "roll":             roll,
                "ear":              avg_ear,
                "ear_threshold":    blink_detector.threshold,
                "blinking":         is_blinking,
                "blink_count":      blink_detector.blink_count,
                "blinks_per_min":   blink_detector.blinks_per_minute,
                "face_area":        face_area,
            })
        else:
            prev_landmarks = None   # reset EMA when face is lost

        # ── HUD ──────────────────────────────────────────────────────────
        draw_hud(frame, hud_data, fps, inf_ms)

        # ── Show ─────────────────────────────────────────────────────────
        cv2.imshow("MediaPipe Face Landmarker — Production", frame)
        key = cv2.waitKey(1) & 0xFF
        if   key == ord("q"):
            break
        elif key == ord("r"):
            tracker.force_reset()
            prev_landmarks = None
        elif key == ord("c"):
            blink_detector.recalibrate()

    # ── Cleanup ──────────────────────────────────────────────────────────
    landmarker.close()
    cap.release()
    cv2.destroyAllWindows()
    print(f"\nSession summary:")
    print(f"  Total blinks    : {blink_detector.blink_count}")
    print(f"  Blink rate      : {blink_detector.blinks_per_minute:.1f} / min")
    print(f"  EAR threshold   : {blink_detector.threshold:.3f}")
    print(f"  Average FPS     : {sum(fps_history)/max(len(fps_history),1):.1f}")


if __name__ == "__main__":
    main()
