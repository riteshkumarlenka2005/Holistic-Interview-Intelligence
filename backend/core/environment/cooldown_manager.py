import time

class CooldownManager:
    def __init__(self):
        self.cooldowns = {}
        
    def is_ready(self, action_key: str, cooldown_seconds: float) -> bool:
        """
        Returns True if the action is ready to be executed (cooldown expired).
        If True, it also resets the cooldown timer automatically.
        """
        now = time.time()
        last_time = self.cooldowns.get(action_key, 0.0)
        
        if now - last_time >= cooldown_seconds:
            self.cooldowns[action_key] = now
            return True
        return False
        
    def time_remaining(self, action_key: str, cooldown_seconds: float) -> float:
        now = time.time()
        last_time = self.cooldowns.get(action_key, 0.0)
        elapsed = now - last_time
        if elapsed >= cooldown_seconds:
            return 0.0
        return cooldown_seconds - elapsed
