import os
import subprocess
from datetime import datetime

# Folder to save videos
save_dir = "/home/sofi/Desktop/headVids"
os.makedirs(save_dir, exist_ok=True)

# Filename with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"headcam_{timestamp}.mp4"
filepath = os.path.join(save_dir, filename)

print(f"Recording video to {filepath} ...")

# Record 10 seconds (10000 ms) of video at 30fps
cmd = [
    "rpicam-vid",
    "-t", "10000",       # duration in ms
    "-o", filepath,      # output file
    "-n"                 # no preview window
]

subprocess.run(cmd, check=True)

print("Recording finished.")
