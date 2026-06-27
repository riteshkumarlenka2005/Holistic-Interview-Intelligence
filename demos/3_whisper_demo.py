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

    # Load model (first run will download ~250MB)
    print("\nLoading Whisper 'small' model (int8 CPU)...")
    model = WhisperModel("small", device="cpu", compute_type="int8")
    print("Model loaded!\n")

    SAMPLE_RATE = 16000
    CHUNK_DURATION = 4  # seconds per chunk
    CHANNELS = 1

    # Filler words to detect
    FILLERS = {"um", "uh", "like", "you know", "basically", "literally", "actually", "sort of", "kind of"}

    total_words = 0
    total_fillers = 0
    total_speaking_time = 0.0
    total_silence_time = 0.0
    total_confidence = 0.0
    total_inference_time = 0.0
    inference_times = []
    successful_chunks = 0
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
                total_silence_time += CHUNK_DURATION
                continue

            chunk_number += 1

            # Save to temp WAV file
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp.close()  # Must close the handle on Windows before reopening with wave
            with wave.open(tmp.name, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio.tobytes())

            # Transcribe
            start = time.perf_counter()
            # Priority 1 & 2: Force English and enable VAD filter
            segments, info = model.transcribe(tmp.name, beam_size=5, language="en", vad_filter=True)
            # Exhaust the generator to force computation
            segments_list = list(segments)
            text = " ".join(s.text.strip() for s in segments_list).strip()
            elapsed = time.perf_counter() - start

            # Clean up temp file
            os.unlink(tmp.name)
            
            # Priority 4: Reject low confidence
            if info.language_probability < 0.5:
                print(f"  Chunk {chunk_number}: (rejected - confidence {info.language_probability:.0%} < 50%)")
                total_silence_time += CHUNK_DURATION
                continue

            # Priority 5: Handle no speech correctly
            if not text:
                print(f"  Chunk {chunk_number}: (no speech detected by VAD)")
                total_silence_time += CHUNK_DURATION
                continue

            # Metrics
            words = text.split()
            word_count = len(words)
            total_words += word_count
            
            # Calculate actual speaking time using VAD/Whisper segment timestamps
            chunk_speaking_time = sum(s.end - s.start for s in segments_list)
            if chunk_speaking_time <= 0:
                chunk_speaking_time = 0.5  # fallback if timestamps are missing but text exists
                
            total_speaking_time += chunk_speaking_time
            total_silence_time += max(0, CHUNK_DURATION - chunk_speaking_time)
            
            successful_chunks += 1
            total_confidence += info.language_probability
            total_inference_time += elapsed
            inference_times.append(elapsed)

            # Filler detection
            text_lower = text.lower()
            chunk_fillers = sum(text_lower.count(f) for f in FILLERS)
            total_fillers += chunk_fillers

            # Priority 3: WPM using Speaking Time instead of Recording Time
            wpm = int((total_words / total_speaking_time) * 60) if total_speaking_time > 0 else 0

            # Pace label (Normal speech is ~120-160)
            if wpm < 100:
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
        # Priority 6: Advanced Session Summary
        print("\n" + "=" * 60)
        print("  SESSION SUMMARY")
        print(f"  Words.............{total_words}")
        print(f"  Fillers...........{total_fillers}")
        print(f"  Speaking Time.....{total_speaking_time:.0f} sec")
        print(f"  Silence Time......{total_silence_time:.0f} sec")
        
        total_time = total_speaking_time + total_silence_time
        speech_ratio = (total_speaking_time / total_time * 100) if total_time > 0 else 0
        print(f"  Speech Ratio......{speech_ratio:.0f}%")
        
        wpm = int((total_words / total_speaking_time) * 60) if total_speaking_time > 0 else 0
        print(f"  Average WPM.......{wpm}")
        
        avg_conf = (total_confidence / successful_chunks * 100) if successful_chunks > 0 else 0
        print(f"  Average Confidence....{avg_conf:.0f}%")
        
        filler_rate = (total_fillers / total_words * 100) if total_words > 0 else 0
        print(f"  Filler rate.......{filler_rate:.1f}%")
        
        avg_inf = (total_inference_time / successful_chunks) if successful_chunks > 0 else 0
        fastest_inf = min(inference_times) if inference_times else 0
        slowest_inf = max(inference_times) if inference_times else 0
        rt_factor = (avg_inf / CHUNK_DURATION) if CHUNK_DURATION > 0 else 0
        
        print("\n  BENCHMARKING")
        print(f"  Model...............small")
        print(f"  Device..............CPU")
        print(f"  Compute.............int8")
        print()
        print(f"  Average inference...{avg_inf:.2f} sec")
        print(f"  Fastest.............{fastest_inf:.2f} sec")
        print(f"  Slowest.............{slowest_inf:.2f} sec")
        print(f"  Realtime factor.....{rt_factor:.2f}x")
        print("=" * 60)


if __name__ == "__main__":
    main()
