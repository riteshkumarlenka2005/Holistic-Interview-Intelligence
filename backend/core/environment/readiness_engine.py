from .models import ReadinessStatus, CameraPillar, CandidatePillar, EnvironmentPillar, ConfidentValue
from .types import EnvironmentState
from .config import WEIGHTS

class ReadinessEngine:
    def evaluate(self, face_data: dict, gaze_data: dict, camera_data: dict, audio_data: dict, bg_data: dict, current_state: EnvironmentState) -> ReadinessStatus:
        
        # 1. Calculate Overall Score
        score = 100
        # Deduct based on individual component logic (simplified for engine)
        if face_data["face_count"].value != 1: score -= WEIGHTS["one_person"]
        if face_data["occlusion"].value != "NONE": score -= WEIGHTS["face_visible"]
        if camera_data["frame_quality_score"] < 50: score -= WEIGHTS["camera"]
        if audio_data["noise_level"].value == "HIGH": score -= WEIGHTS["microphone"]
        if bg_data["status"] == "MESSY": score -= WEIGHTS["background"]
        if face_data["distance"].value != "IDEAL": score -= 5
        
        score = max(0, score)
        
        # 2. Aggregate Blocks & Warnings
        blocks = []
        warnings = []
        
        blocks.extend(face_data.get("blocks", []))
        blocks.extend(camera_data.get("blocks", []))
        blocks.extend(audio_data.get("blocks", []))
        
        warnings.extend(face_data.get("warnings", []))
        warnings.extend(camera_data.get("warnings", []))
        warnings.extend(audio_data.get("warnings", []))
        warnings.extend(bg_data.get("warnings", []))
        warnings.extend(gaze_data.get("warnings", [])) # Informational
        
        # 3. Construct Pillars
        camera_pillar = CameraPillar(
            fps=camera_data["fps"],
            resolution=camera_data["resolution"],
            sharpness=camera_data["sharpness"],
            brightness=camera_data["brightness"],
            exposure=camera_data["exposure"],
            stability=camera_data["stability"],
            frame_quality_score=camera_data["frame_quality_score"]
        )
        
        candidate_pillar = CandidatePillar(
            face_count=face_data["face_count"],
            identity=face_data["identity"],
            face_visibility=face_data["visibility"],
            occlusion=face_data["occlusion"],
            distance=face_data["distance"],
            horizontal_offset=face_data["horizontal_offset"],
            vertical_offset=face_data["vertical_offset"],
            gaze=gaze_data["direction"],
            eye_contact=gaze_data["eye_contact"]
        )
        
        env_pillar = EnvironmentPillar(
            lighting=ConfidentValue(value="GOOD", confidence=100.0), # Derived in UI from camera brightness
            background_clutter=bg_data["clutter_score"],
            noise=audio_data["noise_level"],
            echo=audio_data["echo"],
            multiple_speakers=audio_data["multiple_speakers"]
        )
        
        status = ReadinessStatus(
            state=current_state,
            overall_score=score,
            camera=camera_pillar,
            candidate=candidate_pillar,
            environment=env_pillar,
            blocking_reasons=blocks,
            warnings=warnings
        )
        
        return status
