# controllers/pwm_utils.py
def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def frame_us(freq_hz: int) -> int:
    return int(1_000_000 / freq_hz)

def us_to_duty(pulse_us: int, freq_hz: int) -> float:
    # duty% = (pulse_us / frame_us) * 100
    return (pulse_us / frame_us(freq_hz)) * 100.0

def percent_to_us_bidir(percent: int, min_us=1000, neutral_us=1500, max_us=2000) -> int:
    """Map -100..100 to MIN..MAX with 0 at NEUTRAL."""
    p = clamp(percent, -100, 100)
    return int((p + 100) * (max_us - min_us) / 200 + min_us)

def us_to_percent_bidir(pulse_us: int, min_us=1000, neutral_us=1500, max_us=2000) -> int:
    """Inverse mapping to percent for display."""
    pulse_us = clamp(pulse_us, min_us, max_us)
    return int(round((pulse_us - min_us) * 200 / (max_us - min_us) - 100))
