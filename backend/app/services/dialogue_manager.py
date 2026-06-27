from typing import Dict, Any, List, Optional
import time
from enum import Enum
from app.core.config import settings

class DialogueState(Enum):
    IDLE = "IDLE"
    ASKING_QUESTION = "ASKING_QUESTION"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    COACHING = "COACHING"
    ASKING_NEXT_QUESTION = "ASKING_NEXT_QUESTION"
    FINISHED = "FINISHED"

class DialogueManager:
    """
    Manages the conversational flow, handles TTS queueing, duplicate suppression,
    and interruption (barge-in) logic via a strict state machine.
    """
    def __init__(self):
        self.state = DialogueState.IDLE
        self.coaching_queue: List[Dict[str, Any]] = []
        self.spoken_history: List[str] = []
        self.last_spoken_time: float = 0.0

    def transition_state(self, new_state: DialogueState):
        """Enforce valid state transitions (simplified for now)."""
        self.state = new_state

    def queue_coaching(self, message: str, coaching_type: str, priority: str = "normal"):
        """
        Queues a coaching message. Suppresses semantic duplicates and sets TTL.
        """
        # Semantic duplicate suppression
        for item in self.coaching_queue:
            if item["type"] == coaching_type:
                return # Suppress duplicate
                
        self.coaching_queue.append({
            "message": message,
            "type": coaching_type,
            "priority": priority,
            "queued_at": time.time()
        })

    def process_queue(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves the next valid coaching message to speak. Drops expired messages.
        Returns a DialogueResponse payload for Edge-TTS.
        """
        current_time = time.time()
        
        # Filter out expired messages
        self.coaching_queue = [
            m for m in self.coaching_queue 
            if current_time - m["queued_at"] <= settings.dialogue_queue_ttl
        ]
        
        if not self.coaching_queue:
            return None
            
        # Priority Queue Logic: sort by priority (high > normal > low)
        priority_map = {"high": 3, "normal": 2, "low": 1}
        self.coaching_queue.sort(key=lambda x: priority_map.get(x["priority"], 1), reverse=True)
        
        next_message = self.coaching_queue.pop(0)
        
        # Debounce/Cooldown logic
        if current_time - self.last_spoken_time < settings.coaching_cooldown:
            # Requeue it if it's high priority, otherwise drop
            if priority_map.get(next_message["priority"], 1) == 3:
                self.coaching_queue.insert(0, next_message)
            return None

        # Build DialogueResponse
        response = {
            "text": next_message["message"],
            "emotion": "encouraging",
            "priority": next_message["priority"],
            "interrupt": False
        }
        
        self.last_spoken_time = current_time
        
        # Conversation memory
        self.spoken_history.append(next_message["message"])
        if len(self.spoken_history) > 5:
            self.spoken_history.pop(0)
            
        return response

    def handle_barge_in(self):
        """
        Invoked when the candidate starts speaking while TTS is playing.
        """
        if self.state in [DialogueState.COACHING, DialogueState.ASKING_QUESTION, DialogueState.ASKING_NEXT_QUESTION]:
            self.transition_state(DialogueState.LISTENING)
            # Emit a websocket event to instantly halt TTS playback on the frontend
            return {"action": "STOP_AUDIO"}
        return None
