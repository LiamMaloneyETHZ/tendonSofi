import sys,os

def relativeDir(relPath):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(script_dir)
    dynamixel_control_path = os.path.join(script_dir, relPath)
    print(dynamixel_control_path)
    dynamixel_control_path = os.path.normpath(dynamixel_control_path)
    print(dynamixel_control_path)
    sys.path.append(dynamixel_control_path)