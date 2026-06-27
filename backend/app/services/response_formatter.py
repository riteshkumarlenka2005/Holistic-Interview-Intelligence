import re

class ResponseFormatter:
    """
    Condenses and formats Gemini output into spoken-word ready text for the DialogueManager.
    """
    
    @staticmethod
    def format_coaching_message(strengths: list, weaknesses: list, improvements: list) -> str:
        """
        Takes the raw JSON lists and produces a single concise sentence.
        """
        parts = []
        
        if strengths:
            # Take just the first strength and shorten it
            parts.append(f"Good job on {strengths[0].lower().strip('.')}")
            
        if weaknesses or improvements:
            # Combine weakness/improvement into one concise point
            target = improvements[0] if improvements else weaknesses[0]
            parts.append(f"try to {target.lower().strip('.')}")
            
        if not parts:
            return "Great answer."
            
        return " but ".join(parts) + "."

    @staticmethod
    def clean_for_speech(text: str) -> str:
        """
        Removes markdown, long urls, and simplifies text for TTS.
        """
        if not text:
            return ""
            
        # Remove markdown bold/italic
        text = re.sub(r'[*_]{1,2}', '', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://\S+', 'this link', text)
        
        # Replace common symbols that TTS struggles with
        text = text.replace("&", "and")
        
        return text.strip()
