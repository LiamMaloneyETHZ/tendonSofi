import RPi.GPIO as GPIO
import time

ESC_GPIO = 18
FREQ = 50  # Hz (standard for ESCs)

GPIO.setmode(GPIO.BCM)
GPIO.setup(ESC_GPIO, GPIO.OUT)
pwm = GPIO.PWM(ESC_GPIO, FREQ)
pwm.start(0)  # Start with no signal

def pulse_to_duty(pulse_us):
    return (pulse_us / 20000.0) * 100

MAX_PULSE = 2000
MIN_PULSE = 1000

try:
    print("=== ESC CALIBRATION MODE ===")
    print("1. DISCONNECT the battery from the ESC.")
    input("2. Press [Enter] to send MAX throttle (2000 µs)...")

    pwm.ChangeDutyCycle(pulse_to_duty(MAX_PULSE))
    print("** Now connect the battery. ESC should beep (detecting max throttle)...")
    input("3. Once beeping stops, press [Enter] to send MIN throttle (1000 µs)...")

    pwm.ChangeDutyCycle(pulse_to_duty(MIN_PULSE))
    print("** ESC should confirm with beeps. Calibration complete.")

    time.sleep(2)
    print("4. Returning to idle duty cycle...")
    pwm.ChangeDutyCycle(pulse_to_duty(1100))  # a safe idle value

    print("Calibration done. You may now test throttle manually.")

except KeyboardInterrupt:
    print("\nInterrupted.")

finally:
    pwm.stop()
    GPIO.cleanup()
