import random
import time
from .types import GazeDirection

class ChallengeManager:
    def __init__(self):
        self.challenges = ["BLINK", "TURN_LEFT", "TURN_RIGHT", "LOOK_UP", "LOOK_DOWN", "SMILE"]
        self.active_challenge = None
        self.challenge_start_time = 0
        self.timeout_seconds = 5.0
        
        # State tracking for completion
        self.initial_blinks = 0
        self.challenge_status = "IDLE" # IDLE, ACTIVE, PASSED, FAILED
        
    def trigger_random_challenge(self, current_blinks: int) -> str:
        """Starts a random challenge and returns the prompt text for the UI."""
        self.active_challenge = random.choice(self.challenges)
        self.challenge_start_time = time.time()
        self.initial_blinks = current_blinks
        self.challenge_status = "ACTIVE"
        
        prompts = {
            "BLINK": "Liveness Check: Please blink twice.",
            "TURN_LEFT": "Liveness Check: Please turn your head left.",
            "TURN_RIGHT": "Liveness Check: Please turn your head right.",
            "LOOK_UP": "Liveness Check: Please look up.",
            "LOOK_DOWN": "Liveness Check: Please look down.",
            "SMILE": "Liveness Check: Please smile."
        }
        return prompts[self.active_challenge]
        
    def evaluate(self, current_blinks: int, yaw: float, pitch: float, gaze: GazeDirection, is_smiling: bool) -> str:
        """Evaluates if the candidate has passed the active challenge."""
        if self.challenge_status != "ACTIVE":
            return self.challenge_status
            
        elapsed = time.time() - self.challenge_start_time
        if elapsed > self.timeout_seconds:
            self.challenge_status = "FAILED"
            self.active_challenge = None
            return self.challenge_status
            
        passed = False
        
        if self.active_challenge == "BLINK":
            if current_blinks >= self.initial_blinks + 2:
                passed = True
        elif self.active_challenge == "TURN_LEFT":
            if yaw < -20.0 or gaze == GazeDirection.LEFT:
                passed = True
        elif self.active_challenge == "TURN_RIGHT":
            if yaw > 20.0 or gaze == GazeDirection.RIGHT:
                passed = True
        elif self.active_challenge == "LOOK_UP":
            if pitch < -15.0 or gaze == GazeDirection.UP:
                passed = True
        elif self.active_challenge == "LOOK_DOWN":
            if pitch > 15.0 or gaze == GazeDirection.DOWN:
                passed = True
        elif self.active_challenge == "SMILE":
            if is_smiling:
                passed = True
                
        if passed:
            self.challenge_status = "PASSED"
            self.active_challenge = None
            
        return self.challenge_status
