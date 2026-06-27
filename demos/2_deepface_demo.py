"""
Demo 2: DeepFace Emotion Detection
Tests: Facial emotion recognition from webcam snapshots

Install:  pip install deepface tf-keras opencv-python
Run:      python demos/2_deepface_demo.py
Controls: Press 'q' to quit
"""
import cv2
import time


def main():
    try:
        from deepface import DeepFace
    except ImportError:
        print("ERROR: pip install deepface tf-keras")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Cannot open webcam")
        return

    print("=" * 50)
    print("  DeepFace Emotion Detection Demo")
    print("  Press 'q' to quit")
    print("=" * 50)

    # Label mapping: raw DeepFace → user-friendly interview labels
    LABEL_MAP = {
        "angry": "Frustrated",
        "disgust": "Discomfort",
        "fear": "Interview Nervousness",
        "happy": "Positive / Confident",
        "sad": "Low Engagement",
        "surprise": "Surprised",
        "neutral": "Composed",
    }

    last_result = None
    last_analysis_time = 0
    ANALYSIS_INTERVAL = 1.0  # seconds between analyses (DeepFace is heavy)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        now = time.time()
        if now - last_analysis_time >= ANALYSIS_INTERVAL:
            try:
                results = DeepFace.analyze(
                    frame,
                    actions=["emotion"],
                    enforce_detection=False,
                    silent=True,
                )
                if isinstance(results, list):
                    results = results[0]
                last_result = results
                last_analysis_time = now
            except Exception as e:
                print(f"Analysis error: {e}")

        # Draw results
        if last_result:
            emotions = last_result.get("emotion", {})
            dominant = last_result.get("dominant_emotion", "unknown")
            friendly_label = LABEL_MAP.get(dominant, dominant.title())

            # Draw bounding box if available
            region = last_result.get("region", {})
            if region:
                x, y, w, h = region.get("x", 0), region.get("y", 0), region.get("w", 0), region.get("h", 0)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Dominant emotion header
            cv2.putText(
                frame,
                f"Dominant: {friendly_label}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2,
            )

            # Emotion breakdown bars
            y_pos = 70
            bar_max_width = 200
            for emotion, score in sorted(emotions.items(), key=lambda x: -x[1]):
                label = LABEL_MAP.get(emotion, emotion.title())
                bar_width = int((score / 100.0) * bar_max_width)
                color = (0, 255, 0) if emotion == dominant else (180, 180, 180)

                cv2.putText(frame, f"{label}", (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                cv2.rectangle(frame, (220, y_pos - 12), (220 + bar_width, y_pos + 2), color, -1)
                cv2.putText(frame, f"{score:.1f}%", (430, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)
                y_pos += 25
        else:
            cv2.putText(frame, "Analyzing...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)

        cv2.imshow("DeepFace Emotion Detection Demo", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\nDone.")


if __name__ == "__main__":
    main()
