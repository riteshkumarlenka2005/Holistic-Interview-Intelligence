"""Camera diagnostic v2 — tries every possible approach to get non-black frames."""
import cv2
import time

def test(label, cap, warmup_reads=50, warmup_sleep=0):
    print(f"\n=== {label} ===")
    if not cap.isOpened():
        print("  FAILED to open")
        cap.release()
        return False

    if warmup_sleep > 0:
        time.sleep(warmup_sleep)

    # Warm up by reading frames
    for _ in range(warmup_reads):
        cap.read()

    # Test 3 real frames
    success = False
    for i in range(3):
        ret, frame = cap.read()
        if ret:
            m = frame.mean()
            ok = m > 5
            if ok:
                success = True
            print(f"  Frame {i}: mean={m:.1f} {'[OK - real image!]' if ok else '[BLACK]'}")
        else:
            print(f"  Frame {i}: FAILED to read")

    cap.release()
    return success


# 1. Default (no backend specified)
test("Default (no backend)", cv2.VideoCapture(0), warmup_reads=50, warmup_sleep=2)

# 2. DirectShow
test("DirectShow (DSHOW)", cv2.VideoCapture(0, cv2.CAP_DSHOW), warmup_reads=50, warmup_sleep=2)

# 3. MSMF explicit
test("MSMF explicit", cv2.VideoCapture(0, cv2.CAP_MSMF), warmup_reads=50, warmup_sleep=2)

# 4. DirectShow with MJPG codec
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
test("DirectShow + MJPG", cap, warmup_reads=50, warmup_sleep=2)

# 5. DirectShow with YUY2 codec
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUY2'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
test("DirectShow + YUY2", cap, warmup_reads=50, warmup_sleep=2)

# 6. Very long warm-up
test("DirectShow (5s + 100 frames warmup)", cv2.VideoCapture(0, cv2.CAP_DSHOW), warmup_reads=100, warmup_sleep=5)

# 7. Try opening via filename / device path
test("Device path //./video0", cv2.VideoCapture("//./video0"), warmup_reads=50, warmup_sleep=2)

print("\n=== All tests done ===")
