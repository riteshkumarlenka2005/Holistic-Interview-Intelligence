from fastapi import APIRouter, UploadFile, File
import os
from services.grammar import check_grammar
from services.emotion import analyze_emotion
from faster_whisper import WhisperModel

router = APIRouter()

# Load model once at startup
from faster_whisper import WhisperModel

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)


@router.post("/analyze-speech")
async def analyze_speech(file: UploadFile = File(...)):
    # Ensure temp folder exists
    os.makedirs("temp", exist_ok=True)
    audio_path = f"temp/{file.filename}"
    
    # Save uploaded file
    with open(audio_path, "wb") as f:
        f.write(await file.read())

    # 1. Speech-to-Text using faster-whisper
    segments, info = model.transcribe(audio_path)
    text = " ".join([segment.text for segment in segments])  # Join all segments

    # 2. Grammar check
    grammar = check_grammar(text)

    # 3. Emotion analysis
    emotions = analyze_emotion(text)

    return {"text": text, "grammar": grammar, "emotions": emotions}
