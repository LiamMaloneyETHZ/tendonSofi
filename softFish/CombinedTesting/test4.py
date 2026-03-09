import subprocess
import time
import os
import psutil

# Remove previous signal files safely
signal_file = "/home/srl-slim-tim/Dynamixel_Control/softFish/CombinedTesting/camera_started.txt"
#signal_file2 = "/home/srl-slim-tim/Dynamixel_Control/softFish/CombinedTesting/terminate.txt"

for f in [signal_file]:
    if os.path.exists(f):
        os.remove(f)

print("Starting camtest.py (Camera)...")

#could change to camtest2.py to check new version , had been camtest.py
p1 = subprocess.Popen(["python3", "/home/srl-slim-tim/Dynamixel_Control/softFish/CombinedTesting/camtest.py"])

# Wait for camera to start, then flag sent when camera is started
print("Waiting for camera_started.txt...")
while not os.path.exists(signal_file):
    time.sleep(0.2)

print("Camera signal detected. Launching ForceTimeSerialComm.py and positionControl2.py...")

#had been forcetimeserialcomm2.py
p2 = subprocess.Popen(["python3", "/home/srl-slim-tim/Dynamixel_Control/softFish/CombinedTesting/ForceTimeSerialComm2.py"])

parent_dir = "/home/srl-slim-tim/Dynamixel_Control/softFish"
p3 = subprocess.Popen(["python3", "positionControl3.py"], cwd=parent_dir)

# Give processes some time to start
time.sleep(1)

# Set priorities and affinities

#main change is changing priority and affinity of the processes. Camera should have the highest priority
def set_priority_and_affinity(proc, nice_level=None, cores=None):
    try:
        p = psutil.Process(proc.pid)
        if nice_level is not None:
            # Set priority (nice value)
            p.nice(nice_level)
        if cores is not None:
            # Set CPU affinity
            p.cpu_affinity(cores)
    except Exception as e:
        print(f"Failed to set priority or affinity for PID {proc.pid}: {e}")

# Total cores on system
import multiprocessing
total_cores = multiprocessing.cpu_count()
print(f"Total CPU cores: {total_cores}")

# Define core sets:
# Assign cores 1,2,3,4 (if exist) to process 1
cores_p1 = [1,2,3,4, 5, 6] if total_cores > 6 else list(range(1, total_cores))
# Assign remaining cores to processes 2 and 3
cores_remaining = [c for c in range(total_cores) if c not in cores_p1]

# Set highest priority (nice -10) for camera process
set_priority_and_affinity(p1, nice_level=-10, cores=cores_p1)

# Set default priority and affinity for p2 and p3 to remaining cores
set_priority_and_affinity(p2, nice_level=0, cores=cores_remaining)
set_priority_and_affinity(p3, nice_level=0, cores=cores_remaining)

# Wait for p3 to finish, might not be necessary because p3 sends its own termination signal
p3.wait()
print("positionControl3.py has finished.")

# Clean up
p2.terminate()
p1.terminate()

print("All scripts finished.")
