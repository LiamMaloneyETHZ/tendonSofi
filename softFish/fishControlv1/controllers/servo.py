# controllers/servo.py
import time
import RPi.GPIO as GPIO
from .pwm_utils import clamp, us_to_duty

class ServoController:
    """
    Behavior:
      - 50 Hz default
      - min/center/max microseconds
      - deadband in µs
      - auto idle-off after settle_s (default 0.15s)
      - backwards-compatible: accepts idle_off_s (treated as settle_s)
      - 'hold' toggle keeps pulses active
    """
    def __init__(self, pin=19, freq=50, min_us=500, center_us=1500, max_us=2500,
                 us_deadband=6, idle_off_s=None, settle_s=0.15):
        self.pin = pin
        self.freq = freq
        self.min_us = min_us
        self.center_us = center_us
        self.max_us = max_us
        self.us_deadband = us_deadband

        # Backward compatibility: if caller passes idle_off_s, use it
        if idle_off_s is not None:
            self.settle_s = idle_off_s
        else:
            self.settle_s = settle_s

        GPIO.setup(self.pin, GPIO.OUT)
        self._pwm = GPIO.PWM(self.pin, self.freq)
        self._pwm.start(0)

        self.angle = 90
        self.us = center_us
        self._last_us = None
        self._asleep = True
        self._last_cmd_t = 0
        self._force_hold = False

    def angle_to_us(self, angle: int) -> int:
        angle = clamp(angle, 0, 180)
        span = self.max_us - self.min_us
        return int(self.min_us + (angle / 180.0) * span)

    def _apply_us(self, target_us: int):
        target_us = clamp(target_us, self.min_us, self.max_us)
        if self._last_us is None or abs(target_us - self._last_us) >= self.us_deadband:
            self._pwm.ChangeDutyCycle(us_to_duty(target_us, self.freq))
            self._last_us = target_us
            self._asleep = False
            self._last_cmd_t = time.time()

    def _auto_idle_check(self):
        if not self._force_hold and not self._asleep:
            if (time.time() - self._last_cmd_t) >= self.settle_s:
                self._pwm.ChangeDutyCycle(0)
                self._asleep = True

    def center(self):
        self.angle = 90
        self.us = self.center_us
        self._apply_us(self.center_us)

    def set_angle_step(self, delta_deg: int):
        self.angle = clamp(self.angle + delta_deg, 0, 180)
        self.us = self.angle_to_us(self.angle)
        self._apply_us(self.us)

    def set_angle_abs(self, angle_deg: int):
        self.angle = clamp(angle_deg, 0, 180)
        self.us = self.angle_to_us(self.angle)
        self._apply_us(self.us)

    def toggle_hold(self):
        """Force pulses on/off regardless of auto-idle."""
        if self._force_hold:
            self._force_hold = False
            self._last_cmd_t = time.time()
            return False
        else:
            self._force_hold = True
            if self._last_us:
                self._pwm.ChangeDutyCycle(us_to_duty(self._last_us, self.freq))
                self._asleep = False
            return True

    def maybe_idle_off(self):
        """Keeps compatibility with old main loop call."""
        self._auto_idle_check()

    def stop(self):
        try:
            self._pwm.ChangeDutyCycle(0)
        except Exception:
            pass
        self._pwm.stop()
