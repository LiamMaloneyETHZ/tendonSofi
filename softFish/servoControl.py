#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time, sys, os, tty, termios, argparse

# ---------- Helpers ----------
def read_key():
    if os.name == 'nt':
        import msvcrt
        return msvcrt.getch().decode()
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b' and sys.stdin.read(1) == '[':
            return '\x1b[' + sys.stdin.read(1)  # arrows
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def clamp(v, lo, hi): return max(lo, min(hi, v))

# ---------- Args ----------
ap = argparse.ArgumentParser(description="Software-PWM servo keyboard controller (RPi.GPIO) with idle+deadband.")
ap.add_argument("--pin", type=int, default=19, help="BCM GPIO for servo signal (default: 19)")
ap.add_argument("--freq", type=int, default=50, help="PWM frequency Hz (default: 50)")
ap.add_argument("--min_us", type=int, default=500, help="Min pulse width (µs)")
ap.add_argument("--center_us", type=int, default=1500, help="Center pulse width (µs)")
ap.add_argument("--max_us", type=int, default=2500, help="Max pulse width (µs)")
ap.add_argument("--step", type=int, default=5, help="Angle step for ←/→ (deg)")
ap.add_argument("--idle_off", type=float, default=2.0, help="Seconds idle before PWM off (0 = never)")
ap.add_argument("--us_deadband", type=int, default=6, help="Only update if change ≥ this many µs")
args = ap.parse_args()

FRAME_US = int(1_000_000 / args.freq)  # e.g., 20,000 µs at 50 Hz

def us_to_duty(pulse_us: int) -> float:
    return (pulse_us / FRAME_US) * 100.0

def angle_to_us(angle: int) -> int:
    angle = clamp(angle, 0, 180)
    span = args.max_us - args.min_us
    return int(args.min_us + (angle/180.0)*span)

# ---------- GPIO ----------
GPIO.setmode(GPIO.BCM)
GPIO.setup(args.pin, GPIO.OUT)
pwm = GPIO.PWM(args.pin, args.freq)
pwm.start(0)

print(f"Servo on GPIO{args.pin} @ {args.freq} Hz  |  {args.min_us}-{args.center_us}-{args.max_us} µs")
print("Controls: ←/→ ±step | ↑/↓ ±15° | [ / ] ±90° | c=center | h=hold on/off | q=quit")
print(f"Idle-off: {args.idle_off}s (0 disables). Press [Enter] to arm at center...")

angle = 90
us = args.center_us
last_us = None
last_key_time = time.time()
asleep = False

def apply_us(target_us: int):
    global last_us, asleep
    target_us = clamp(target_us, args.min_us, args.max_us)
    if asleep or last_us is None or abs(target_us - last_us) >= args.us_deadband:
        pwm.ChangeDutyCycle(us_to_duty(target_us))
        last_us = target_us
        asleep = False

try:
    while True:
        k = read_key()
        if k in ('\r', '\n'):
            apply_us(args.center_us)
            angle = 90
            us = args.center_us
            print(f"Armed at center ({args.center_us} µs).")
            last_key_time = time.time()
            break

    while True:
        k = read_key()

        if   k == '\x1b[C': angle = clamp(angle + args.step, 0, 180); us = angle_to_us(angle)
        elif k == '\x1b[D': angle = clamp(angle - args.step, 0, 180); us = angle_to_us(angle)
        elif k == '\x1b[A': angle = clamp(angle + 15, 0, 180);       us = angle_to_us(angle)
        elif k == '\x1b[B': angle = clamp(angle - 15, 0, 180);       us = angle_to_us(angle)
        elif k == ']':      angle = clamp(angle + 90, 0, 180);       us = angle_to_us(angle)
        elif k == '[':      angle = clamp(angle - 90, 0, 180);       us = angle_to_us(angle)
        elif k == 'c':      angle = 90;                              us = args.center_us
        elif k == 'h':
            if asleep:
                apply_us(us)
                print("\rHold ON (pulses active)      ", end="")
            else:
                pwm.ChangeDutyCycle(0)
                asleep = True
                print("\rHold OFF (pulses stopped)     ", end="")
            last_key_time = time.time()
            continue
        elif k == 'q':
            print("\nBye.")
            break

        apply_us(us)
        last_key_time = time.time()
        print(f"\rAngle: {angle:3d}°  →  {us} µs   ", end="", flush=True)

        if args.idle_off > 0 and not asleep and (time.time() - last_key_time) >= args.idle_off:
            pwm.ChangeDutyCycle(0)
            asleep = True
            print("\rIdle → pulses OFF                 ", end="", flush=True)

        time.sleep(0.01)

finally:
    pwm.ChangeDutyCycle(0)
    pwm.stop()
    GPIO.cleanup()
