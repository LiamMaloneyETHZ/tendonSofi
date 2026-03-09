# fishControlv1/controllers/__init__.py

"""Controllers package: servo, ESC, UPS monitor, and PWM helpers."""

from .servo import ServoController
from .esc import ESCController
from .ups import UPSMonitor, make_ina219_read_fn
from .pwm_utils import (
    clamp,
    frame_us,
    us_to_duty,
    percent_to_us_bidir,
    us_to_percent_bidir,
)

__all__ = [
    "ServoController",
    "ESCController",
    "UPSMonitor",
    "make_ina219_read_fn",
    "clamp",
    "frame_us",
    "us_to_duty",
    "percent_to_us_bidir",
    "us_to_percent_bidir",
]

__version__ = "1.0.1"
