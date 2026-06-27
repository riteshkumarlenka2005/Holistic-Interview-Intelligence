from enum import Enum

class EnvironmentState(str, Enum):
    CHECKING = "CHECKING"
    READY = "READY"
    INTERVIEW_RUNNING = "INTERVIEW_RUNNING"
    WARNING = "WARNING"
    BLOCKED = "BLOCKED"
    RECOVERED = "RECOVERED"

class GazeDirection(str, Enum):
    CENTER = "CENTER"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    UP = "UP"
    DOWN = "DOWN"

class IdentityStatus(str, Enum):
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    UNCERTAIN = "UNCERTAIN"
    NO_FACE = "NO_FACE"

class CameraStability(str, Enum):
    STABLE = "STABLE"
    MODERATE = "MODERATE"
    SHAKY = "SHAKY"
    
class DistanceStatus(str, Enum):
    IDEAL = "IDEAL"
    TOO_CLOSE = "TOO_CLOSE"
    TOO_FAR = "TOO_FAR"
    
class EchoLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
