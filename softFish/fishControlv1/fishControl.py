#!/usr/bin/env python3
# fishControlv1/fishControl.py

import os, sys, time, argparse, csv
import RPi.GPIO as GPIO

# --- Path bootstrap so this file can be run directly (python3 fishControl.py) ---
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PARENT_DIR = os.path.dirname(_THIS_DIR)
if _PARENT_DIR not in sys.path:
    sys.path.insert(0, _PARENT_DIR)
# -------------------------------------------------------------------------------

from fishControlv1.io.keyboard import RawKeyboard
from fishControlv1.controllers.servo import ServoController
from fishControlv1.controllers.esc import ESCController
from fishControlv1.controllers.ups import UPSMonitor, make_ina219_read_fn

def _now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()) + f".{int((time.time()%1)*1000):03d}"

def _make_logfile_path(base_dir):
    os.makedirs(base_dir, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M", time.localtime())
    return os.path.join(base_dir, f"{stamp}_fishTest.csv")

def main():
    ap = argparse.ArgumentParser(description="Keyboard control: Servo + Bidirectional ESC + UPS monitor (CSV logging)")
    # Default pins
    ap.add_argument("--servo-pin", type=int, default=19, help="BCM pin for servo signal (default: 19)")
    ap.add_argument("--esc-pin", type=int, default=18, help="BCM pin for ESC signal (default: 18)")
    ap.add_argument("--freq", type=int, default=50, help="PWM frequency Hz (default: 50)")

    # Servo defaults (unchanged behavior)
    ap.add_argument("--servo-min-us", type=int, default=500)
    ap.add_argument("--servo-center-us", type=int, default=1500)
    ap.add_argument("--servo-max-us", type=int, default=2500)
    ap.add_argument("--servo-step", type=int, default=5)
    ap.add_argument("--servo-us-deadband", type=int, default=6)
    ap.add_argument("--servo-idle-off", type=float, default=2.0)

    # ESC defaults (unchanged behavior)
    ap.add_argument("--esc-min-us", type=int, default=1000)
    ap.add_argument("--esc-neutral-us", type=int, default=1500)
    ap.add_argument("--esc-max-us", type=int, default=2000)
    ap.add_argument("--esc-step-pct", type=int, default=5)

    # UPS + logging
    ap.add_argument("--ups-interval", type=float, default=0.5, help="Seconds between UPS polls")
    ap.add_argument("--log-dir", default="/home/sofi/TestingData", help="Directory to save CSV logs")
    ap.add_argument("--log-interval", type=float, default=0.5, help="Seconds between CSV samples")
    # Optional: override INA219 bus/address if needed (defaults match your sample)
    ap.add_argument("--ina-bus", type=int, default=1, help="I2C bus number for INA219 (default: 1)")
    ap.add_argument("--ina-addr", type=lambda x: int(x, 0), default=0x41, help="I2C address (e.g., 0x41)")

    args = ap.parse_args()

    GPIO.setmode(GPIO.BCM)
    servo = esc = ups = None
    csv_file = None
    csv_writer = None
    last_log_t = 0.0
    t0 = time.time()
    armed = False

    fieldnames = [
        "ts_iso","t_s","voltage_V","current_A","power_W",
        "servo_angle_deg","servo_us","servo_hold","esc_percent","esc_us"
    ]
    logfile_path = _make_logfile_path(args.log_dir)

    try:
        # Controllers
        servo = ServoController(
            pin=args.servo_pin, freq=args.freq,
            min_us=args.servo_min_us, center_us=args.servo_center_us, max_us=args.servo_max_us,
            us_deadband=args.servo_us_deadband, idle_off_s=args.servo_idle_off,
        )
        esc = ESCController(
            pin=args.esc_pin, freq=args.freq,
            min_us=args.esc_min_us, neutral_us=args.esc_neutral_us, max_us=args.esc_max_us,
        )

        # UPS monitor (using integrated INA219 reader)
        UPS_READ_FN = make_ina219_read_fn(i2c_bus=args.ina_bus, addr=args.ina_addr)
        ups = UPSMonitor(read_fn=UPS_READ_FN, interval_s=args.ups_interval)
        ups.start()

        # CSV
        csv_file = open(logfile_path, "w", newline="")
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_file.flush()
        print(f"[LOG] Writing to {logfile_path}")

        print("=== Dual Controller ===")
        print(f"Servo: GPIO{args.servo_pin} @ {args.freq} Hz  |  {args.servo_min_us}-{args.servo_center_us}-{args.servo_max_us} µs")
        print(f"ESC:   GPIO{args.esc_pin}   @ {args.freq} Hz  |  {args.esc_min_us}-{args.esc_neutral_us}-{args.esc_max_us} µs\n")
        print("Controls:")
        print("  [Enter]  Arm both (servo=center, ESC=neutral)")
        print("  Servo:   d=+step | a=-step | w=+15° | s=-15° | e=+90° | q=-90° | c=center | h=hold on/off")
        print("  ESC:     t=+5%  | g=-5%   | x=neutral | p=set percent (-100..100)")
        print("  z        Quit\n")
        print("Waiting for [Enter] to arm...")

        with RawKeyboard() as kb:
            # Arm on Enter
            while not armed:
                k = kb.read_key(timeout=0.05)
                if k in ('\n', '\r'):
                    servo.center()
                    esc.arm_neutral()
                    armed = True
                    print("Armed: servo centered, ESC neutral.")
                time.sleep(0.01)

            # Main loop
            while True:
                k = kb.read_key(timeout=0.05)

                if k:
                    # Servo keys
                    if   k == 'd':
                        servo.set_angle_step(+args.servo_step)
                    elif k == 'a':
                        servo.set_angle_step(-args.servo_step)
                    elif k == 'w':
                        servo.set_angle_step(+15)
                    elif k == 's':
                        servo.set_angle_step(-15)
                    elif k == 'e':
                        servo.set_angle_step(+90)
                    elif k == 'q':
                        servo.set_angle_step(-90)
                    elif k == 'c':
                        servo.center()
                    elif k == 'h':
                        on = servo.toggle_hold()
                        print("\rServo hold: " + ("ON (pulses active)   " if on else "OFF (pulses stopped) "), end="")

                    # ESC keys
                    elif k == 't':
                        esc.step_percent(+args.esc_step_pct)
                    elif k == 'g':
                        esc.step_percent(-args.esc_step_pct)
                    elif k == 'x':
                        esc.neutral()
                    elif k == 'p':
                        try:
                            line = kb.input_line("\nEnter throttle % (-100..100): ")
                            val = int(line.strip())
                            esc.set_percent(val)
                        except Exception:
                            print("Invalid percent.")

                    # Quit
                    elif k == 'z':
                        print(f"\nBye. Log saved to: {logfile_path}")
                        break

                # Servo idle-off
                _ = servo.maybe_idle_off()

                # Status line
                v, a = ups.get() if ups else (None, None)
                watts = (abs(v * a) if (v is not None and a is not None) else None)
                if watts is not None:
                    status = (f"\rServo {servo.angle:3d}° → {servo.us:4d}µs"
                              f"   |   ESC {esc.throttle_percent:>4d}% → {esc.throttle_us:4d}µs"
                              f"   |   UPS {v:>5.2f}V {a:>5.2f}A {watts:>6.2f}W")
                else:
                    status = (f"\rServo {servo.angle:3d}° → {servo.us:4d}µs"
                              f"   |   ESC {esc.throttle_percent:>4d}% → {esc.throttle_us:4d}µs"
                              f"   |   UPS --")
                print(status, end="", flush=True)

                # CSV logging
                now = time.time()
                if (now - last_log_t) >= args.log_interval and csv_writer:
                    angle = getattr(servo, "angle", None)
                    servo_us = getattr(servo, "us", None)
                    servo_hold = getattr(servo, "_asleep", False)
                    esc_pct = getattr(esc, "throttle_percent", None)
                    esc_us = getattr(esc, "throttle_us", None)

                    v_cell = "" if v is None else round(float(v), 4)
                    a_cell = "" if a is None else round(float(a), 4)
                    w_cell = "" if watts is None else round(float(watts), 4)

                    row = {
                        "ts_iso": _now_iso(),
                        "t_s": round(now - t0, 3),
                        "voltage_V": v_cell,
                        "current_A": a_cell,
                        "power_W":   w_cell,
                        "servo_angle_deg": angle,
                        "servo_us": servo_us,
                        "servo_hold": bool(servo_hold),
                        "esc_percent": esc_pct,
                        "esc_us": esc_us,
                    }
                    csv_writer.writerow(row)
                    csv_file.flush()
                    last_log_t = now

                time.sleep(0.01)

    finally:
        try:
            if ups: ups.stop()
        except Exception:
            pass
        try:
            if esc: esc.stop()
        except Exception:
            pass
        try:
            if servo: servo.stop()
        except Exception:
            pass
        try:
            if csv_file:
                csv_file.flush()
                csv_file.close()
        except Exception:
            pass
        GPIO.cleanup()

if __name__ == "__main__":
    main()
