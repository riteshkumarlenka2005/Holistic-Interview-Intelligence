# Facial Emotion Recognition Audit

Based on a detailed analysis of your backend codebase, here is the current state of Facial Emotion Recognition in your architecture.

## 1. Library Status
- **Is DeepFace already installed?** ❌ No. It is not present in `requirements.txt` or imported anywhere in the backend codebase.
- **Is FER already installed?** ✅ Yes. It is pinned in your `requirements.txt` (`fer==22.5.1`) and imported in the backend.
- **Which library is actually used?** The backend currently uses **FER** (`from fer.fer import FER`).

## 2. Implementation Details
- **Which files perform facial emotion recognition?** The logic is entirely isolated within `backend/app/services/behavioral_analysis.py`.
- **Is emotion detection active?** ✅ Yes. It is fully implemented and actively called by the `behavioral_ws.py` WebSocket.
- **What emotions are currently detected?** 7 emotions: `happy`, `neutral`, `fear`, `sad`, `angry`, `surprise`, and `disgust`. These are aggregated into `confidence_score` and `nervousness_score`.
- **Is the input the full frame or a cropped face?** Currently, it passes the **full frame** (`self.detector.detect_emotions(frame)`). FER does its own internal face detection to find the face before scoring emotions.
- **How often is it executed?** It runs per-frame as they stream in via the WebSocket.

## 3. Performance Analysis (CPU Optimization)
**Is the implementation CPU optimized?** ❌ **No. It is highly unoptimized.**
Because FER is being passed the full frame, it runs its own internal face detector (MTCNN) to find the face first. 
At the same time, your new `VisionPipeline` (Phase 2) is *also* running MediaPipe to find the face on the exact same frame. 
**You are running two heavy ML face detectors simultaneously on a CPU.**

## 4. Recommendation: Replace FER with DeepFace

I recommend **Replacing FER with DeepFace** for your CPU-only FastApi architecture.

**Why DeepFace?**
DeepFace has a critical feature for CPU optimization: `enforce_detection=False`. 
Because your `VisionPipeline` already finds the face bounding box instantly using MediaPipe, you can simply crop the frame to the face and pass *only the cropped face* to DeepFace with `enforce_detection=False`. 
This bypasses DeepFace's internal face detector entirely, cutting the CPU workload in half. FER does not make this architectural pattern as easy or reliable to implement.

### Required Architectural Changes
If we proceed with DeepFace, the pipeline should look like this:

1. **Uninstall FER**: Remove `fer` from `requirements.txt`.
2. **Install DeepFace**: Add `deepface` to `requirements.txt`.
3. **Refactor Pipeline**: 
   - Extract the bounding box from `VisionPipeline` (MediaPipe).
   - Crop the `numpy` array to that bounding box.
   - Send the cropped, 224x224 image directly into DeepFace's emotion classifier (`DeepFace.analyze(cropped_img, actions=['emotion'], enforce_detection=False)`).
4. **Deprecate Legacy File**: Completely retire the old `behavioral_analysis.py` file, migrating its confidence/nervousness math into a new lightweight `EmotionEngine` that plugs into your `VisionPipeline`.
