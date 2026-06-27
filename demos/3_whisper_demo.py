"""
Demo 3: Faster-Whisper Live Transcription
Tests: Microphone input → real-time transcription, speaking speed (WPM), pause detection

Install:  pip install faster-whisper sounddevice numpy
Run:      python demos/3_whisper_demo.py
Controls: Ctrl+C to stop
"""
import time
import tempfile
import wave
import os
import numpy as np


def main():
    try:
        import sounddevice as sd
    except ImportError:
        print("ERROR: pip install sounddevice")
        return

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("ERROR: pip install faster-whisper")
        return

    print("=" * 50)
    print("  Faster-Whisper Live Transcription Demo")
    print("  Speak into your microphone")
    print("  Ctrl+C to stop")
    print("=" * 50)

    # Load model (first run will download ~150MB)
    print("\nLoading Whisper 'base' model (int8 CPU)...")
    model = WhisperModel("base", device="cpu", compute_type="int8")
    print("Model loaded!\n")

    SAMPLE_RATE = 16000
    CHUNK_DURATION = 4  # seconds per chunk
    CHANNELS = 1

    # Filler words to detect
    FILLERS = {"um", "uh", "like", "you know", "basically", "literally", "actually", "sort of", "kind of"}

    total_words = 0
    total_fillers = 0
    total_duration = 0.0
    chunk_number = 0

    print("Listening... (speak now)\n")
    print("-" * 60)

    try:
        while True:
            # Record a chunk
            audio = sd.rec(
                int(SAMPLE_RATE * CHUNK_DURATION),
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype="int16",
            )
            sd.wait()

            # Check if there's actual audio (not silence)
            rms = np.sqrt(np.mean(audio.astype(np.float32) ** 2))
            if rms < 100:
                print("  (silence)")
                continue

            chunk_number += 1

            # Save to temp WAV file
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            with wave.open(tmp.name, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio.tobytes())

            # Transcribe
            start = time.perf_counter()
            segments, info = model.transcribe(tmp.name, beam_size=5)
            text = " ".join(s.text.strip() for s in segments).strip()
            elapsed = time.perf_counter() - start

            # Clean up temp file
            os.unlink(tmp.name)

            if not text:
                print(f"  Chunk {chunk_number}: (no speech detected)")
                continue

            # Metrics
            words = text.split()
            word_count = len(words)
            total_words += word_count
            total_duration += CHUNK_DURATION

            # Filler detection
            text_lower = text.lower()
            chunk_fillers = sum(text_lower.count(f) for f in FILLERS)
            total_fillers += chunk_fillers

            # WPM
            wpm = int((total_words / total_duration) * 60) if total_duration > 0 else 0

            # Pace label
            if wpm < 80:
                pace = "TOO SLOW"
            elif wpm > 180:
                pace = "TOO FAST"
            else:
                pace = "GOOD"

            # Display
            print(f"  Chunk {chunk_number}:")
            print(f"    Text:     \"{text}\"")
            print(f"    Language: {info.language} ({info.language_probability:.0%})")
            print(f"    Words:    {word_count} | Fillers: {chunk_fillers}")
            print(f"    Speed:    {wpm} WPM ({pace})")
            print(f"    Whisper:  {elapsed:.2f}s inference")
            print()

    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("  SESSION SUMMARY")
        print(f"  Total words:   {total_words}")
        print(f"  Total fillers: {total_fillers}")
        print(f"  Duration:      {total_duration:.0f}s")
        wpm = int((total_words / total_duration) * 60) if total_duration > 0 else 0
        print(f"  Average WPM:   {wpm}")
        filler_rate = (total_fillers / total_words * 100) if total_words > 0 else 0
        print(f"  Filler rate:   {filler_rate:.1f}%")
        print("=" * 60)


if __name__ == "__main__":
    main()
