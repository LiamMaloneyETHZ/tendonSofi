# controllers/esc.py
import RPi.GPIO as GPIO
from .pwm_utils import clamp, percent_to_us_bidir, us_to_duty, us_to_percent_bidir

class ESCController:
    """
    Mirrors your brushlessControl.py behavior (bidirectional):
      - 50 Hz default
      - MIN/NEUTRAL/MAX in µs (1000/1500/2000)
      - w/s step throttle, x neutral, p set % (-100..100)
    """
    def __init__(self, pin=18, freq=50, min_us=1000, neutral_us=1500, max_us=2000):
        self.pin = pin
        self.freq = freq
        self.min_us = min_us
        self.neutral_us = neutral_us
        self.max_us = max_us

        GPIO.setup(self.pin, GPIO.OUT)
        self._pwm = GPIO.PWM(self.pin, self.freq)
        self._pwm.start(0)

        self._throttle_us = self.neutral_us

    def _apply_us(self, pulse_us: int):
        pulse_us = clamp(pulse_us, self.min_us, self.max_us)
        self._throttle_us = pulse_us
        self._pwm.ChangeDutyCycle(us_to_duty(pulse_us, self.freq))

    def arm_neutral(self):
        self._apply_us(self.neutral_us)

    def step_percent(self, delta_pct: int):
        pct = us_to_percent_bidir(self._throttle_us, self.min_us, self.neutral_us, self.max_us)
        pct = clamp(pct + delta_pct, -100, 100)
        self.set_percent(pct)

    def set_percent(self, pct: int):
        us = percent_to_us_bidir(pct, self.min_us, self.neutral_us, self.max_us)
        self._apply_us(us)

    def neutral(self):
        self._apply_us(self.neutral_us)

    @property
    def throttle_us(self) -> int:
        return self._throttle_us

    @property
    def throttle_percent(self) -> int:
        return us_to_percent_bidir(self._throttle_us, self.min_us, self.neutral_us, self.max_us)

    def stop(self):
        try:
            self._pwm.ChangeDutyCycle(0)
        except Exception:
            pass
        self._pwm.stop()
