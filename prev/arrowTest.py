import sys
import msvcrt

while True:
    key = msvcrt.getch()
    if key == b'\xe0':
        next_key = msvcrt.getch()
        if next_key == b'H':
            print("Up Arrow")
        elif next_key == b'P':
            print("Down Arrow")
        elif next_key == b'K':
            print("Left Arrow")
        elif next_key == b'M':
            print("Right Arrow")
        else:
            print(f"Unknown key: {key + next_key}")
    else:
        sys.exit()
