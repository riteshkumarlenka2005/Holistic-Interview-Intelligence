from .models import IntegrityReport
from .utils import RollingAverage

class IntegrityTracker:
    def __init__(self):
        # We track integrity drops using 30s rolling averages 
        # so brief mistakes don't permanently ruin the score.
        self.identity_score = RollingAverage(30)
        self.eye_focus_score = RollingAverage(30)
        self.face_count_score = RollingAverage(30)
        self.speaker_count_score = RollingAverage(30)
        self.environment_score = RollingAverage(30)

        # Initialize perfectly
        self.identity_score.add(100.0)
        self.eye_focus_score.add(100.0)
        self.face_count_score.add(100.0)
        self.speaker_count_score.add(100.0)
        self.environment_score.add(100.0)

    def update(self, identity_ok: bool, looking_at_screen: bool, single_face: bool, single_speaker: bool, env_ok: bool):
        self.identity_score.add(100.0 if identity_ok else 0.0)
        self.eye_focus_score.add(100.0 if looking_at_screen else 0.0)
        self.face_count_score.add(100.0 if single_face else 0.0)
        self.speaker_count_score.add(100.0 if single_speaker else 0.0)
        self.environment_score.add(100.0 if env_ok else 0.0)

    def get_report(self) -> IntegrityReport:
        id_score = int(self.identity_score.get_average())
        focus_score = int(self.eye_focus_score.get_average())
        face_score = int(self.face_count_score.get_average())
        speak_score = int(self.speaker_count_score.get_average())
        env_score = int(self.environment_score.get_average())

        # Overall is an average of the sub-components
        overall = int((id_score + focus_score + face_score + speak_score + env_score) / 5)

        return IntegrityReport(
            identity=id_score,
            eye_focus=focus_score,
            multiple_faces=face_score,
            multiple_speakers=speak_score,
            environment=env_score,
            overall_integrity=overall
        )
