import sys
import os

def relativeDirUp(levels=1):
    # Get the absolute path of the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up 'levels' times
    for _ in range(levels):
        script_dir = os.path.dirname(script_dir)
    # Normalize the path
    script_dir = os.path.normpath(script_dir)
    # Add to sys.path
    sys.path.append(script_dir)
