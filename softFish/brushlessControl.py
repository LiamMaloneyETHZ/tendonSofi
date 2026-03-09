import RPi.GPIO as GPIO
import time
import sys
import os
import tty
import termios

# GPIO settings
ESC_GPIO = 18
FREQ = 50  # Hz

# ESC PWM range
MIN_PULSE = 1000  # Full reverse
NEUTRAL   = 1500  # Stop
MAX_PULSE = 2000  # Full forward

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(ESC_GPIO, GPIO.OUT)
pwm = GPIO.PWM(ESC_GPIO, FREQ)
pwm.start(0)

# Convert microseconds to duty cycle %
def pulse_to_duty(pulse_us):
    return (pulse_us / 20000.0) * 100

# Convert percent (-100 to 100) to µs
def percent_to_us(percent):
    percent = max(-100, min(100, percent))
    return int((percent + 100) * 5 + 1000)

# Cross-platform key reader
def readKey():
    if os.name == 'nt':
        import msvcrt
        return msvcrt.getch().decode()
    else:
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

# Initialize
throttle_us = NEUTRAL
print("=== Bidirectional ESC Controller ===")
print("Keys:")
print("  [Enter] → Arm ESC (send NEUTRAL)")
print("  w → Increase throttle (+5%)")
print("  s → Decrease throttle (-5%)")
print("  x → Full stop (1500 µs)")
print("  p → Set throttle as % (-100 to 100)")
print("  q → Quit")
print()

print("Waiting for [Enter] to arm...")
while True:
    key = readKey()
    if key == '\r' or key == '\n':
        pwm.ChangeDutyCycle(pulse_to_duty(NEUTRAL))
        print("ESC armed at NEUTRAL (1500 µs)")
        break

try:
    while True:
        key = readKey()

        if key == 'w':
            throttle_us = min(throttle_us + 25, MAX_PULSE)
            pwm.ChangeDutyCycle(pulse_to_duty(throttle_us))
            print(f"Throttle ↑ {throttle_us} µs")

        elif key == 's':
            throttle_us = max(throttle_us - 25, MIN_PULSE)
            pwm.ChangeDutyCycle(pulse_to_duty(throttle_us))
            print(f"Throttle ↓ {throttle_us} µs")

        elif key == 'x':
            throttle_us = NEUTRAL
            pwm.ChangeDutyCycle(pulse_to_duty(NEUTRAL))
            print("Neutral stop (1500 µs)")

        elif key == 'p':
            try:
                val = int(input("Enter throttle % (-100 to 100): "))
                throttle_us = percent_to_us(val)
                pwm.ChangeDutyCycle(pulse_to_duty(throttle_us))
                print(f"Throttle set to {val}% → {throttle_us} µs")
            except:
                print("Invalid input.")

        elif key == 'q':
            print("Quitting...")
            break

        time.sleep(0.05)

finally:
    pwm.stop()
    GPIO.cleanup()
