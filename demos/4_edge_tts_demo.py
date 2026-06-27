"""
Demo 4: Edge-TTS Text-to-Speech
Tests: Convert text to natural-sounding speech and play it

Install:  pip install edge-tts
Run:      python demos/4_edge_tts_demo.py
"""
import asyncio
import tempfile
import os
import subprocess
import sys


async def speak(text: str, voice: str = "en-US-AriaNeural"):
    """Generate speech from text and play it."""
    import edge_tts

    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.close()

    print(f"  Voice:  {voice}")
    print(f"  Text:   \"{text}\"")
    print(f"  Generating audio...")

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(tmp.name)

    file_size = os.path.getsize(tmp.name)
    print(f"  File:   {tmp.name} ({file_size:,} bytes)")

    # Try to play the audio
    print(f"  Playing...")
    try:
        if sys.platform == "win32":
            # Windows: use the built-in media player
            os.startfile(tmp.name)
        elif sys.platform == "darwin":
            subprocess.run(["afplay", tmp.name], check=True)
        else:
            subprocess.run(["mpv", "--no-video", tmp.name], check=True)
    except Exception as e:
        print(f"  Could not auto-play: {e}")
        print(f"  Manually open: {tmp.name}")

    return tmp.name


async def main():
    try:
        import edge_tts
    except ImportError:
        print("ERROR: pip install edge-tts")
        return

    print("=" * 50)
    print("  Edge-TTS Text-to-Speech Demo")
    print("=" * 50)

    # Demo 1: Interview question
    print("\n--- Interview Question ---")
    await speak(
        "Can you explain the difference between a process and a thread, "
        "and when you would choose one over the other?"
    )

    await asyncio.sleep(3)

    # Demo 2: Coaching hint
    print("\n--- Coaching Hint ---")
    await speak(
        "Try to maintain eye contact with the camera and reduce filler words.",
        voice="en-US-AriaNeural",
    )

    await asyncio.sleep(3)

    # Demo 3: List available voices
    print("\n--- Available English Voices ---")
    voices = await edge_tts.list_voices()
    english_voices = [v for v in voices if v["Locale"].startswith("en-")]
    for v in english_voices[:10]:
        print(f"  {v['ShortName']:30s}  {v['Gender']:8s}  {v['Locale']}")
    print(f"  ... and {len(english_voices) - 10} more")

    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
