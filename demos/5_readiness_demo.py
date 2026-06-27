import cv2
import time
import mediapipe as mp
import numpy as np
import sys
import os
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.environment.face_validator import FaceValidator
from backend.core.environment.gaze_analyzer import GazeAnalyzer
from backend.core.environment.camera_analyzer import CameraAnalyzer
from backend.core.environment.audio_analyzer import AudioAnalyzer
from backend.core.environment.background_analyzer import BackgroundAnalyzer
from backend.core.environment.utils import RollingAverage
from backend.core.environment.readiness_engine import ReadinessEngine
from backend.core.environment.state_machine import ReadinessStateMachine
from backend.core.environment.types import EnvironmentState

# Phase 5.6 Modules
from backend.core.environment.trigger_engine import TriggerEngine
from backend.core.environment.identity_service import IdentityService
from backend.core.environment.challenge_manager import ChallengeManager
from backend.core.environment.cooldown_manager import CooldownManager

# Landmark indices
LEFT_EYE_OUTER = 33
LEFT_EYE_RIGHT = 133
LEFT_EYE_TOP = 159
LEFT_EYE_BOTTOM = 145
LEFT_IRIS_CENTER = 468
NOSE_TIP = 1
CHIN = 152
LEFT_MOUTH = 61
RIGHT_MOUTH = 291

def calculate_gaze_ratios(landmarks, w, h):
    outer = landmarks[LEFT_EYE_OUTER]
    inner = landmarks[LEFT_EYE_RIGHT]
    top = landmarks[LEFT_EYE_TOP]
    bottom = landmarks[LEFT_EYE_BOTTOM]
    iris = landmarks[LEFT_IRIS_CENTER]
    
    eye_width = abs(outer.x - inner.x)
    eye_height = abs(bottom.y - top.y)
    
    if eye_width == 0 or eye_height == 0: return 0.5, 0.5
        
    horiz = (iris.x - min(outer.x, inner.x)) / eye_width
    vert = (iris.y - min(top.y, bottom.y)) / eye_height
    return horiz, vert

def calculate_head_pose(landmarks, w, h):
    indices = [NOSE_TIP, CHIN, LEFT_EYE_OUTER, 263, LEFT_MOUTH, RIGHT_MOUTH]
    face_2d = []
    face_3d = []
    for idx in indices:
        lm = landmarks[idx]
        x, y = int(lm.x * w), int(lm.y * h)
        face_2d.append([x, y])
        face_3d.append([x, y, lm.z])
    face_2d = np.array(face_2d, dtype=np.float64)
    face_3d = np.array(face_3d, dtype=np.float64)
    cam_matrix = np.array([[w, 0, w / 2], [0, w, h / 2], [0, 0, 1]])
    dist = np.zeros((4, 1), dtype=np.float64)
    ok, rot_vec, _ = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist)
    if ok:
        rmat, _ = cv2.Rodrigues(rot_vec)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
        return angles[0] * 360, angles[1] * 360, angles[2] * 360
    return 0.0, 0.0, 0.0

def main():
    print("=" * 50)
    print("  Phase 5.6: Anti-Spoofing & Trigger Engine Demo")
    print("  Booting up...")
    print("=" * 50)

    face_val = FaceValidator()
    gaze_ana = GazeAnalyzer()
    cam_ana = CameraAnalyzer()
    aud_ana = AudioAnalyzer()
    bg_ana = BackgroundAnalyzer()
    engine = ReadinessEngine()
    machine = ReadinessStateMachine()
    
    trigger_engine = TriggerEngine()
    identity_svc = IdentityService()
    challenge_mgr = ChallengeManager()
    cooldown_mgr = CooldownManager()
    
    fps_smoother = RollingAverage(window_size_seconds=2.0)
    horiz_smoother = RollingAverage(window_size_seconds=0.5)
    vert_smoother = RollingAverage(window_size_seconds=0.5)

    mp_mesh = mp.solutions.face_mesh
    face_mesh = mp_mesh.FaceMesh(max_num_faces=10, refine_landmarks=True)

    cap = cv2.VideoCapture(0)
    last_frame_time = time.time()
    blinks = 0
    was_blinking = False
    
    anchor_set = False
    
    print("\n[READY] Press 's' to set your Anchor Photo and start the interview.")

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        now = time.time()
        fps = 1.0 / (now - last_frame_time + 1e-6)
        last_frame_time = now
        fps_smoother.add(fps)
        
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 1. MediaPipe
        results = face_mesh.process(rgb)
        lm_list = results.multi_face_landmarks if results.multi_face_landmarks else []
        
        pitch, yaw, roll = 0, 0, 0
        is_smiling = False
        
        if lm_list:
            lm = lm_list[0].landmark
            pitch, yaw, roll = calculate_head_pose(lm, w, h)
            
            # Simple Blink and Smile for Challenges
            top = lm[LEFT_EYE_TOP]
            bottom = lm[LEFT_EYE_BOTTOM]
            eye_h = math.sqrt((top.x-bottom.x)**2 + (top.y-bottom.y)**2)
            left = lm[33]
            right = lm[133]
            eye_w = math.sqrt((left.x-right.x)**2 + (left.y-right.y)**2)
            ear = eye_h / eye_w if eye_w > 0 else 0
            if ear < 0.2:
                if not was_blinking: blinks += 1
                was_blinking = True
            else:
                was_blinking = False
                
            mouth_w = math.sqrt((lm[LEFT_MOUTH].x-lm[RIGHT_MOUTH].x)**2 + (lm[LEFT_MOUTH].y-lm[RIGHT_MOUTH].y)**2)
            if mouth_w > 0.35 * w: # Very crude smile detection
                is_smiling = True
            
        # 2. Phase 5 Analyzers
        # Extract face_bbox for background analyzer
        face_bbox = None
        if lm_list:
            xs = [p.x for p in lm_list[0].landmark]
            ys = [p.y for p in lm_list[0].landmark]
            face_bbox = (int(min(xs)*w), int(min(ys)*h), int(max(xs)*w), int(max(ys)*h))
            
        bg_data = bg_ana.process(frame, face_bbox)
        face_data = face_val.process(lm_list, frame, w, h, None)
        cam_data = cam_ana.process(gray, fps_smoother.get_average())
        aud_data = aud_ana.process(rms_noise=50, volume=85, overlapping_speakers=False)
        
        # Gaze tracking
        gaze_data = gaze_ana.process(0.5, 0.5)
        if lm_list:
            try:
                raw_horiz, raw_vert = calculate_gaze_ratios(lm_list[0].landmark, w, h)
                horiz_smoother.add(raw_horiz)
                vert_smoother.add(raw_vert)
                gaze_data = gaze_ana.process(horiz_smoother.get_average(), vert_smoother.get_average())
            except: pass
        
        # 3. Phase 5.6 Trigger Engine
        fc = face_data["face_count"].value
        is_new = face_data.get("is_new_candidate", False)
        area = face_data.get("face_area", 0.0)
        
        triggers = trigger_engine.evaluate(fc, is_new, area)
        
        id_result = identity_svc.get_latest_result()
        
        if anchor_set:
            if triggers and cooldown_mgr.is_ready("deepface_verify", cooldown_seconds=30.0):
                # Trigger fired, let's run DeepFace in background!
                identity_svc.run_verification_async(frame)
                
            # Check Identity results
            # If liveness fails, trigger a physical Challenge
            if id_result["anti_spoof"] is False and id_result["last_updated"] > 0:
                if challenge_mgr.challenge_status == "IDLE":
                    challenge_mgr.trigger_random_challenge(blinks)
                    
            # If Identity Verification failed, block the interview
            if id_result["last_updated"] > 0 and not id_result["identity"]:
                if "Identity Mismatch: Unregistered candidate detected" not in face_data["blocks"]:
                    face_data["blocks"].append("Identity Mismatch: Unregistered candidate detected")
                    
            # 4. Evaluate Challenge Response
            if challenge_mgr.challenge_status == "ACTIVE":
                status = challenge_mgr.evaluate(blinks, yaw, pitch, gaze_data["direction"].value, is_smiling)
                if status == "FAILED":
                    face_data["blocks"].append("Failed Liveness Challenge")
                    
        # 5. Readiness Engine Output
        status = engine.evaluate(face_data, gaze_data, cam_data, aud_data, bg_data, machine.state)
        
        machine.update_state(
            is_blocked=len(status.blocking_reasons) > 0,
            has_warnings=len(status.warnings) > 0
        )
        status.state = machine.state
        
        # 6. Terminal Dashboard
        print("\033c", end="") # Clear terminal
        print("==============================")
        print("Interview Readiness (Phase 5.6)")
        print("==============================\n")
        
        c = status.camera
        print("Camera")
        print(f"├── FPS              : {int(c.fps.value)} (Conf: {c.fps.confidence}%)")
        print(f"├── Resolution       : {c.resolution}")
        print(f"├── Frame Quality    : {c.frame_quality_score}%")
        print(f"├── Stability        : {c.stability.value.value}\n")
        
        can = status.candidate
        dist_str = f"{can.distance.value.value} (Area: {face_data.get('face_area', 0)*100:.1f}%)"
        pos_str = f"H: {can.horizontal_offset.value:+.1f}%, V: {can.vertical_offset.value:+.1f}%"
        
        id_state = "VERIFIED" if id_result.get("identity") else "UNCERTAIN" if not anchor_set else "MISMATCH"
        
        print("Candidate")
        print(f"├── Face Count       : {can.face_count.value}")
        print(f"├── Identity         : {id_state}")
        print(f"├── Distance         : {dist_str}")
        print(f"├── Position         : {pos_str}")
        print(f"├── Occlusion        : {can.occlusion.value}")
        print(f"├── Gaze             : {can.gaze.value.value} (Conf: {can.gaze.confidence}%)\n")
        
        env = status.environment
        light_stat = "POOR" if c.brightness.value < 40 or c.brightness.value > 220 else "GOOD"
        print("Environment")
        print(f"├── Lighting         : {light_stat}")
        print(f"├── Clutter Score    : {env.background_clutter.value}")
        print(f"├── Noise            : {env.noise.value}")
        print(f"├── Echo             : {env.echo.value.value}")
        
        print("\n------------------------------")
        print(f"Readiness     {status.overall_score}/100")
        print(f"Status        {status.state.value}")
        print("==============================")
        
        if status.blocking_reasons:
            print("\nBLOCKERS:")
            for b in status.blocking_reasons: print(f" ❌ {b}")
        if status.warnings:
            print("\nWARNINGS:")
            for w in status.warnings: print(f" ⚠️ {w}")
            
        if triggers:
            print(f"\n[TRIGGERS FIRED]: {triggers}")
        if challenge_mgr.challenge_status == "ACTIVE":
            print(f"\n[LIVENESS CHALLENGE]: {challenge_mgr.active_challenge}")
        
        # UI Overlay
        disp_frame = frame.copy()
        if challenge_mgr.challenge_status == "ACTIVE":
            cv2.putText(disp_frame, challenge_mgr.active_challenge, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if not anchor_set:
            cv2.putText(disp_frame, "Press 's' to set anchor and start", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
        cv2.imshow("Readiness Frame", disp_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            print("\n[ANCHOR SET] Interview starting...")
            identity_svc.set_anchor(frame)
            anchor_set = True
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
