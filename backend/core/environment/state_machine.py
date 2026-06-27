from typing import List, Dict
from .types import EnvironmentState

class ReadinessStateMachine:
    def __init__(self):
        self.state = EnvironmentState.CHECKING
        
    def update_state(self, is_blocked: bool, has_warnings: bool) -> EnvironmentState:
        """
        Transitions the state machine based on current frame blocks/warnings.
        Valid transitions:
        CHECKING -> READY | BLOCKED
        READY -> INTERVIEW_RUNNING
        INTERVIEW_RUNNING -> WARNING | BLOCKED
        WARNING -> INTERVIEW_RUNNING | BLOCKED
        BLOCKED -> RECOVERED
        RECOVERED -> INTERVIEW_RUNNING | WARNING
        """
        if self.state == EnvironmentState.CHECKING:
            if is_blocked:
                self.state = EnvironmentState.BLOCKED
            else:
                self.state = EnvironmentState.READY
                
        elif self.state == EnvironmentState.READY:
            if is_blocked:
                self.state = EnvironmentState.BLOCKED
            elif has_warnings:
                self.state = EnvironmentState.WARNING
            # Note: Transition to INTERVIEW_RUNNING is handled externally
            
        elif self.state in (EnvironmentState.INTERVIEW_RUNNING, EnvironmentState.WARNING, EnvironmentState.RECOVERED):
            if is_blocked:
                self.state = EnvironmentState.BLOCKED
            elif has_warnings:
                self.state = EnvironmentState.WARNING
            else:
                self.state = EnvironmentState.INTERVIEW_RUNNING
                
        elif self.state == EnvironmentState.BLOCKED:
            if not is_blocked:
                if has_warnings:
                    self.state = EnvironmentState.WARNING
                else:
                    self.state = EnvironmentState.RECOVERED
                    
        return self.state
