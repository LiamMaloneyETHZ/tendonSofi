#!/usr/bin/env python3
# fishControlv1/esc_calibrate.py
#
# ESC calibration helper:
#  1) Guides you through MAX -> power-on -> MIN -> NEUTRAL calibration.
#  2) Interactive test mode to nudge pulse width in microseconds so you can
#     see whether values <1000us or >2000us have any effect on your ESC.
#
# Usage:
#   python3 -m fishControlv1.esc_calibrate --pin 18
#   (adjust --pin and other args as needed)

import time
import argparse
import RPi.GPIO as GPIO

def frame_us(freq_hz: int) -> int:
    return int(1_000_000 / freq_hz)

def us_to_duty(pulse_us: int, freq_hz: int) -> float:
    return (pulse_us / frame_us(freq_hz)) * 100.0

def clamp(v, lo, hi): return max(lo, min(hi, v))

def set_pulse(pwm, freq, pulse_us):
    pwm.ChangeDutyCycle(us_to_duty(pulse_us, freq))

def run_calibration(pwm, freq, min_us, neutral_us, max_us, max_hold, min_hold, neutral_hold):
    print("\n=== ESC Calibration ===")
    print("1) DISCONNECT ESC POWER.")
    print("2) Press [Enter] here; I will output MAX throttle.")
    print("3) QUICKLY CONNECT ESC POWER while I hold MAX. Wait for beeps.")
    print("4) I will then switch to MIN. Wait for beeps.")
    print("5) I will then go to NEUTRAL. Calibration done.")

    input("Press [Enter] to set MAX and begin...")
    print(f" → MAX {max_us} µs")
    set_pulse(pwm, freq, max_us)
    time.sleep(max_hold)

    print(f" → MIN {min_us} µs")
    set_pulse(pwm, freq, min_us)
    time.sleep(min_hold)

    print(f" → NEUTRAL {neutral_us} µs")
    set_pulse(pwm, freq, neutral_us)
    time.sleep(neutral_hold)

    print("Calibration sequence complete.\n")

def interactive_test(pwm, freq, min_us, neutral_us, max_us, start_us=None):
    print("=== Interactive Pulse Test ===")
    print("Type commands, then [Enter]. Examples:")
    print("  min           -> set pulse to configured MIN")
    print("  max           -> set pulse to configured MAX")
    print("  neut          -> set pulse to NEUTRAL")
    print("  set 1200      -> set an absolute pulse in µs")
    print("  up 25         -> increase pulse by 25 µs")
    print("  down 25       -> decrease pulse by 25 µs")
    print("  show          -> print current pulse")
    print("  q             -> quit test\n")

    current_us = neutral_us if start_us is None else int(start_us)
    set_pulse(pwm, freq, current_us)
    print(f"Starting at {current_us} µs")

    while True:
        try:
            line = input("cmd> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting test.")
            break

        if not line:
            continue
        parts = line.split()
        cmd = parts[0].lower()

        try:
            if cmd == "q":
                print("Bye.")
                break
            elif cmd == "min":
                current_us = int(min_us)
                set_pulse(pwm, freq, current_us)
                print(f"pulse = {current_us} µs")
            elif cmd == "max":
                current_us = int(max_us)
                set_pulse(pwm, freq, current_us)
                print(f"pulse = {current_us} µs")
            elif cmd in ("neut", "neutral"):
                current_us = int(neutral_us)
                set_pulse(pwm, freq, current_us)
                print(f"pulse = {current_us} µs")
            elif cmd == "set" and len(parts) >= 2:
                val = int(parts[1])
                current_us = val
                set_pulse(pwm, freq, current_us)
                print(f"pulse = {current_us} µs")
            elif cmd == "up" and len(parts) >= 2:
                delta = int(parts[1])
                current_us += delta
                set_pulse(pwm, freq, current_us)
                print(f"pulse = {current_us} µs")
            elif cmd == "down" and len(parts) >= 2:
                delta = int(parts[1])
                current_us -= delta
                set_pulse(pwm, freq, current_us)
                print(f"pulse = {current_us} µs")
            elif cmd == "show":
                print(f"pulse = {current_us} µs")
            else:
                print("Unknown command. Try: min | max | neut | set N | up N | down N | show | q")
        except Exception as e:
            print(f"Error: {e}")

def main():
    ap = argparse.ArgumentParser(description="ESC calibration + interactive pulse test")
    ap.add_argument("--pin", type=int, default=18, help="BCM GPIO for ESC signal (default: 18)")
    ap.add_argument("--freq", type=int, default=50, help="PWM frequency Hz (default: 50)")
    ap.add_argument("--min-us", type=int, default=1000, help="Nominal MIN pulse (µs)")
    ap.add_argument("--neutral-us", type=int, default=1500, help="Neutral pulse (µs)")
    ap.add_argument("--max-us", type=int, default=2000, help="Nominal MAX pulse (µs)")
    ap.add_argument("--max-hold", type=float, default=3.0, help="Seconds to hold MAX during calibration")
    ap.add_argument("--min-hold", type=float, default=3.0, help="Seconds to hold MIN during calibration")
    ap.add_argument("--neutral-hold", type=float, default=1.5, help="Seconds to hold NEUTRAL after calibration")
    ap.add_argument("--skip-cal", action="store_true", help="Skip calibration, go straight to interactive test")
    ap.add_argument("--start-us", type=int, default=None, help="Start pulse for test (µs)")

    args = ap.parse_args()

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(args.pin, GPIO.OUT)
    pwm = GPIO.PWM(args.pin, args.freq)
    pwm.start(0.0)

    try:
        if not args.skip_cal:
            run_calibration(
                pwm, args.freq,
                args.min_us, args.neutral_us, args.max_us,
                args.max_hold, args.min_hold, args.neutral_hold
            )
        interactive_test(
            pwm, args.freq,
            args.min_us, args.neutral_us, args.max_us,
            start_us=args.start_us
        )
    finally:
        try:
            pwm.ChangeDutyCycle(0.0)
            pwm.stop()
        except Exception:
            pass
        GPIO.cleanup()

if __name__ == "__main__":
    main()
