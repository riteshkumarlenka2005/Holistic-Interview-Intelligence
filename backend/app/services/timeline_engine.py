from typing import List, Dict, Any
from app.models.responses import Response
from app.models.integrity import IntegrityEvent
from datetime import datetime, timezone

class TimelineEngine:
    """
    Generates a chronological event log of the interview milestones.
    """
    
    def generate_timeline(
        self, 
        session_started_at: datetime, 
        responses: List[Response], 
        integrity_events: List[IntegrityEvent],
        session_ended_at: datetime = None
    ) -> List[Dict[str, Any]]:
        events = []
        
        # 1. Start Event
        events.append({
            "timestamp_ms": 0,
            "time_display": "00:00",
            "type": "interview_started",
            "description": "Interview Started"
        })
        
        # 2. Response Events
        # Calculate time offset for each response
        for resp in responses:
            # We approximate response timestamp if asked_at not fully preserved,
            # or we can use question.asked_at. We assume Responses have a chronological order.
            # Here we can generate milestones based on scores.
            offset_ms = 0
            if resp.created_at and session_started_at:
                offset_ms = int((resp.created_at.replace(tzinfo=timezone.utc) - session_started_at.replace(tzinfo=timezone.utc)).total_seconds() * 1000)
            
            time_display = self._format_ms(offset_ms)
            
            # Milestone: Strong Technical Answer
            if resp.technical_score and resp.technical_score >= 85:
                events.append({
                    "timestamp_ms": offset_ms,
                    "time_display": time_display,
                    "type": "strong_answer",
                    "description": "Strong Technical Answer",
                    "details": f"Score: {int(resp.technical_score)}"
                })
            
            # Milestone: Confidence Drop
            if resp.communication_score and resp.communication_score < 50:
                events.append({
                    "timestamp_ms": offset_ms,
                    "time_display": time_display,
                    "type": "confidence_drop",
                    "description": "Confidence Drop",
                    "details": f"Communication score dropped to {int(resp.communication_score)}"
                })

        # 3. Integrity Events
        for ie in integrity_events:
            offset_ms = ie.timestamp_ms
            if offset_ms is None and ie.timestamp and session_started_at:
                offset_ms = int((ie.timestamp.replace(tzinfo=timezone.utc) - session_started_at.replace(tzinfo=timezone.utc)).total_seconds() * 1000)
            
            time_display = self._format_ms(offset_ms) if offset_ms else "00:00"
            
            desc_map = {
                "tab_switch": "Tab Switched",
                "window_blur": "Window Lost Focus",
                "distraction_event": "Distraction Event (Look away)",
                "multiple_faces": "Multiple Faces Detected"
            }
            
            events.append({
                "timestamp_ms": offset_ms or 0,
                "time_display": time_display,
                "type": ie.event_type,
                "description": desc_map.get(ie.event_type, ie.event_type),
                "details": ie.details
            })
            
        # 4. End Event
        end_offset_ms = 0
        if session_ended_at and session_started_at:
             end_offset_ms = int((session_ended_at.replace(tzinfo=timezone.utc) - session_started_at.replace(tzinfo=timezone.utc)).total_seconds() * 1000)
        
        if end_offset_ms > 0:
            events.append({
                "timestamp_ms": end_offset_ms,
                "time_display": self._format_ms(end_offset_ms),
                "type": "interview_ended",
                "description": "Interview Completed"
            })
            
        # Sort by timestamp
        events.sort(key=lambda x: x["timestamp_ms"])
        
        return events

    def _format_ms(self, ms: int) -> str:
        seconds = ms // 1000
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
