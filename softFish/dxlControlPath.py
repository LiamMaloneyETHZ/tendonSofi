import sys, os

def relativeDir(relPath):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.normpath(os.path.join(script_dir, relPath))

    if target_path not in sys.path:
        sys.path.append(target_path)

    return target_path
