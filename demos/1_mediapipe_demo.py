"""
Demo 1: MediaPipe Face Landmarker
Tests: Face detection, face count, eye tracking, head pose (pitch/yaw/roll), blink detection

Install:  pip install mediapipe opencv-python numpy
Run:      python demos/1_mediapipe_demo.py
Controls: Press 'q' to quit
"""
import cv2
import numpy as np
import math
import mediapipe as mp

# --- Landmark indices ---
# Head pose
NOSE_TIP = 1
CHIN = 152
LEFT_EYE_OUTER = 33
RIGHT_EYE_OUTER = 263
LEFT_MOUTH = 61
RIGHT_MOUTH = 291

# Blink detection (Eye Aspect Ratio)
LEFT_EYE_TOP = 159
LEFT_EYE_BOTTOM = 145
LEFT_EYE_LEFT = 33
LEFT_EYE_RIGHT = 133
RIGHT_EYE_TOP = 386
RIGHT_EYE_BOTTOM = 374
RIGHT_EYE_LEFT = 362
RIGHT_EYE_RIGHT = 263

# Iris (requires refine_landmarks=True)
LEFT_IRIS_CENTER = 468
RIGHT_IRIS_CENTER = 473


def calculate_ear(landmarks, top, bottom, left, right, w, h):
    """Eye Aspect Ratio — drops below threshold during blink."""
    vertical = math.sqrt(
        (landmarks[top].x * w - landmarks[bottom].x * w) ** 2
        + (landmarks[top].y * h - landmarks[bottom].y * h) ** 2
    )
    horizontal = math.sqrt(
        (landmarks[left].x * w - landmarks[right].x * w) ** 2
        + (landmarks[left].y * h - landmarks[right].y * h) ** 2
    )
    return vertical / horizontal if horizontal > 0 else 0


def calculate_gaze_ratios(landmarks, w, h):
    """Calculate horizontal and vertical gaze ratios using iris center."""
    # Use person's left eye (indices 33 to 133)
    outer = landmarks[LEFT_EYE_OUTER]
    inner = landmarks[LEFT_EYE_RIGHT]
    top = landmarks[LEFT_EYE_TOP]
    bottom = landmarks[LEFT_EYE_BOTTOM]
    iris = landmarks[LEFT_IRIS_CENTER]
    
    # 0.0 to 1.0 from screen left to screen right
    eye_width = abs(outer.x - inner.x)
    eye_height = abs(bottom.y - top.y)
    
    if eye_width == 0 or eye_height == 0:
        return 0.5, 0.5
        
    horiz = (iris.x - min(outer.x, inner.x)) / eye_width
    vert = (iris.y - min(top.y, bottom.y)) / eye_height
    
    return horiz, vert


def calculate_head_pose(landmarks, w, h):
    """SolvePnP head pose estimation → pitch, yaw, roll in degrees."""
    indices = [NOSE_TIP, CHIN, LEFT_EYE_OUTER, RIGHT_EYE_OUTER, LEFT_MOUTH, RIGHT_MOUTH]
    face_2d, face_3d = [], []
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
    mp_mesh = mp.solutions.face_mesh
    face_mesh = mp_mesh.FaceMesh(
        max_num_faces=2,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    draw_utils = mp.solutions.drawing_utils
    draw_styles = mp.solutions.drawing_styles

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Cannot open webcam")
        return

    blink_count = 0
    EAR_THRESHOLD = 0.20
    was_blinking = False

    print("=" * 50)
    print("  MediaPipe Face Landmarker Demo")
    print("  Press 'q' to quit")
    print("=" * 50)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = face_mesh.process(rgb)

        if results.multi_face_landmarks:
            face_count = len(results.multi_face_landmarks)
            lm = results.multi_face_landmarks[0].landmark

            # Draw mesh on first face
            draw_utils.draw_landmarks(
                frame,
                results.multi_face_landmarks[0],
                mp_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=draw_styles.get_default_face_mesh_tesselation_style(),
            )

            # Head pose
            pitch, yaw, roll = calculate_head_pose(lm, w, h)

            # Gaze
            horiz, vert = calculate_gaze_ratios(lm, w, h)
            if horiz < 0.40: gaze_dir = "RIGHT"
            elif horiz > 0.60: gaze_dir = "LEFT"
            elif vert < 0.38: gaze_dir = "UP"
            elif vert > 0.65: gaze_dir = "DOWN"
            else: gaze_dir = "CENTER"
            
            looking = (gaze_dir == "CENTER")

            # Draw Iris and Gaze Vector
            for iris_idx in [LEFT_IRIS_CENTER, RIGHT_IRIS_CENTER]:
                iris = lm[iris_idx]
                ix, iy = int(iris.x * w), int(iris.y * h)
                cv2.circle(frame, (ix, iy), 2, (0, 255, 0), -1)
                
                # Draw vector (amplified for visibility)
                dx = int((horiz - 0.5) * 150)
                dy = int((vert - 0.5) * 150)
                cv2.arrowedLine(frame, (ix, iy), (ix + dx, iy + dy), (0, 0, 255), 2, tipLength=0.3)

            # Blink (EAR)
            left_ear = calculate_ear(lm, LEFT_EYE_TOP, LEFT_EYE_BOTTOM, LEFT_EYE_LEFT, LEFT_EYE_RIGHT, w, h)
            right_ear = calculate_ear(lm, RIGHT_EYE_TOP, RIGHT_EYE_BOTTOM, RIGHT_EYE_LEFT, RIGHT_EYE_RIGHT, w, h)
            avg_ear = (left_ear + right_ear) / 2
            is_blinking = avg_ear < EAR_THRESHOLD
            if is_blinking and not was_blinking:
                blink_count += 1
            was_blinking = is_blinking

            # --- HUD overlay ---
            overlay = [
                f"Eye Contact: {'YES' if looking else 'NO'}",
                f"Gaze Direction: {gaze_dir} (H: {horiz-0.5:+.2f}, V: {vert-0.5:+.2f})",
                f"Blinks: {blink_count}  (EAR {avg_ear:.3f})",
                f"Pitch: {pitch:+.1f} deg",
                f"Yaw:   {yaw:+.1f} deg",
            ]
            y = 30
            for line in overlay:
                color = (0, 255, 0) if ("YES" in line or "CENTER" in line) else (0, 200, 255)
                cv2.putText(frame, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)
                y += 28
        else:
            cv2.putText(frame, "No face detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        cv2.imshow("MediaPipe Face Landmarker Demo", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"\nSession summary: {blink_count} blinks detected.")


if __name__ == "__main__":
    main()
