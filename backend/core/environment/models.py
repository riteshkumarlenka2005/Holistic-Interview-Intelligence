from pydantic import BaseModel, Field
from typing import List, Optional, Any
from .types import EnvironmentState, IdentityStatus, GazeDirection, CameraStability, DistanceStatus, EchoLevel

# --- Confidence Wrappers ---
class ConfidentValue(BaseModel):
    value: Any
    confidence: float = Field(ge=0.0, le=100.0)

# --- Four Pillars ---
class CameraPillar(BaseModel):
    fps: ConfidentValue
    resolution: str
    sharpness: ConfidentValue
    brightness: ConfidentValue
    exposure: ConfidentValue
    stability: ConfidentValue  # CameraStability
    frame_quality_score: int

class CandidatePillar(BaseModel):
    face_count: ConfidentValue
    identity: ConfidentValue   # IdentityStatus
    face_visibility: ConfidentValue
    occlusion: ConfidentValue  # str describing occlusion
    distance: ConfidentValue   # DistanceStatus
    horizontal_offset: ConfidentValue
    vertical_offset: ConfidentValue
    gaze: ConfidentValue       # GazeDirection
    eye_contact: ConfidentValue

class EnvironmentPillar(BaseModel):
    lighting: ConfidentValue
    background_clutter: ConfidentValue
    noise: ConfidentValue
    echo: ConfidentValue       # EchoLevel
    multiple_speakers: ConfidentValue

# --- Overall Output ---
class ReadinessStatus(BaseModel):
    state: EnvironmentState
    overall_score: int
    camera: CameraPillar
    candidate: CandidatePillar
    environment: EnvironmentPillar
    blocking_reasons: List[str]
    warnings: List[str]

class IntegrityReport(BaseModel):
    identity: int = 100
    eye_focus: int = 100
    multiple_faces: int = 100
    multiple_speakers: int = 100
    environment: int = 100
    overall_integrity: int = 100
