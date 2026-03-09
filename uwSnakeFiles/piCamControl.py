import os, time, threading, sys, termios, tty, subprocess, signal
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder

# --- CONFIG ---
SAVE_DIR = "/home/uwpi/Desktop/Camera"
os.makedirs(SAVE_DIR, exist_ok=True)

# --- GLOBALS ---
recording = False
recording_thread = None
picam2 = Picamera2()

# Default resolution and framerate
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30

def record_video():
    global recording
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    base_name = f"video_{timestamp}_{VIDEO_WIDTH}x{VIDEO_HEIGHT}@{VIDEO_FPS}"
    h264_path = os.path.join(SAVE_DIR, f"{base_name}.h264")
    mp4_path = os.path.join(SAVE_DIR, f"{base_name}.mp4")

    print(f"[INFO] Starting video recording to {h264_path}")
    config = picam2.create_video_configuration(main={"size": (VIDEO_WIDTH, VIDEO_HEIGHT)}, controls={"FrameRate": VIDEO_FPS})
    picam2.configure(config)
    encoder = H264Encoder()
    picam2.start_recording(encoder, output=h264_path)

    while recording:
        time.sleep(0.5)

    picam2.stop_recording()
    print(f"[INFO] Recording stopped and saved to {h264_path}")

    print(f"[INFO] Converting to MP4: {mp4_path}")
    try:
        subprocess.run([
            "ffmpeg", "-y", "-framerate", str(VIDEO_FPS),
            "-i", h264_path,
            "-c:v", "copy", mp4_path
        ], check=True)
        print(f"[INFO] Conversion complete: {mp4_path}")
        os.remove(h264_path)
    except subprocess.CalledProcessError:
        print("[ERROR] ffmpeg conversion failed.")

def take_snapshot():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(SAVE_DIR, f"snapshot_{timestamp}.jpg")
    config = picam2.create_still_configuration(main={"size": (VIDEO_WIDTH, VIDEO_HEIGHT)})
    picam2.configure(config)
    picam2.start()
    time.sleep(1)
    picam2.capture_file(filename)
    picam2.stop()
    print(f"[INFO] Snapshot saved: {filename}")

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def handle_exit(signum, frame):
    global recording
    print("\n[INFO] Caught termination signal. Cleaning up...")
    if recording:
        recording = False
        recording_thread.join()
    print("[INFO] Exiting safely.")
    sys.exit(0)

# --- MAIN LOOP ---
if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_exit)   # Ctrl+C
    signal.signal(signal.SIGTERM, handle_exit)  # kill

    print(f"[INFO] Ready. Video resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT} @ {VIDEO_FPS} FPS")
    print("""
[CONTROLS]
  r → Start recording
  s → Stop recording
  p → Take snapshot
  q → Quit
""")

    while True:
        key = get_key()
        if key == 'r' and not recording:
            recording = True
            recording_thread = threading.Thread(target=record_video, daemon=True)
            recording_thread.start()

        elif key == 's' and recording:
            recording = False
            recording_thread.join()

        elif key == 'p':
            take_snapshot()

        elif key == 'q':
            if recording:
                print("[INFO] Stopping recording before quitting.")
                recording = False
                recording_thread.join()
            print("[INFO] Exiting.")
            break