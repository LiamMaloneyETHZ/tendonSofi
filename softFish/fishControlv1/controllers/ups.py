# fishControlv1/controllers/ups.py
import threading
import time
import math
from typing import Optional, Tuple, Callable

# ---------- Your INA219 register-level driver (as provided) ----------

import smbus

# Registers
_REG_CONFIG                 = 0x00
_REG_SHUNTVOLTAGE           = 0x01
_REG_BUSVOLTAGE             = 0x02
_REG_POWER                  = 0x03
_REG_CURRENT                = 0x04
_REG_CALIBRATION            = 0x05

class BusVoltageRange:
    RANGE_16V = 0x00
    RANGE_32V = 0x01

class Gain:
    DIV_1_40MV  = 0x00
    DIV_2_80MV  = 0x01
    DIV_4_160MV = 0x02
    DIV_8_320MV = 0x03

class ADCResolution:
    ADCRES_9BIT_1S    = 0x00
    ADCRES_10BIT_1S   = 0x01
    ADCRES_11BIT_1S   = 0x02
    ADCRES_12BIT_1S   = 0x03
    ADCRES_12BIT_2S   = 0x09
    ADCRES_12BIT_4S   = 0x0A
    ADCRES_12BIT_8S   = 0x0B
    ADCRES_12BIT_16S  = 0x0C
    ADCRES_12BIT_32S  = 0x0D
    ADCRES_12BIT_64S  = 0x0E
    ADCRES_12BIT_128S = 0x0F

class Mode:
    POWERDOW             = 0x00
    SVOLT_TRIGGERED      = 0x01
    BVOLT_TRIGGERED      = 0x02
    SANDBVOLT_TRIGGERED  = 0x03
    ADCOFF               = 0x04
    SVOLT_CONTINUOUS     = 0x05
    BVOLT_CONTINUOUS     = 0x06
    SANDBVOLT_CONTINUOUS = 0x07

class INA219:
    def __init__(self, i2c_bus=1, addr=0x40):
        self.bus = smbus.SMBus(i2c_bus)
        self.addr = addr
        self._cal_value = 0
        self._current_lsb = 0
        self._power_lsb = 0
        # self.set_calibration_32V_2A()
        self.set_calibration_16V_5A()

    def read(self, address):
        data = self.bus.read_i2c_block_data(self.addr, address, 2)
        return ((data[0] * 256) + data[1])

    def write(self, address, data):
        temp = [0, 0]
        temp[1] = data & 0xFF
        temp[0] = (data & 0xFF00) >> 8
        self.bus.write_i2c_block_data(self.addr, address, temp)

    def set_calibration_32V_2A(self):
        self._current_lsb = .1    # mA/bit
        self._cal_value = 4096
        self._power_lsb = .002    # W/bit
        self.write(_REG_CALIBRATION, self._cal_value)
        self.bus_voltage_range = BusVoltageRange.RANGE_32V
        self.gain = Gain.DIV_8_320MV
        self.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        self.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        self.mode = Mode.SANDBVOLT_CONTINUOUS
        self.config = (self.bus_voltage_range << 13 |
                       self.gain << 11 |
                       self.bus_adc_resolution << 7 |
                       self.shunt_adc_resolution << 3 |
                       self.mode)
        self.write(_REG_CONFIG, self.config)

    def set_calibration_16V_5A(self):
        self._current_lsb = 0.1524   # mA/bit
        self._cal_value = 26868
        self._power_lsb = 0.003048   # W/bit
        self.write(_REG_CALIBRATION, self._cal_value)
        self.bus_voltage_range = BusVoltageRange.RANGE_16V
        self.gain = Gain.DIV_2_80MV
        self.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        self.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        self.mode = Mode.SANDBVOLT_CONTINUOUS
        self.config = (self.bus_voltage_range << 13 |
                       self.gain << 11 |
                       self.bus_adc_resolution << 7 |
                       self.shunt_adc_resolution << 3 |
                       self.mode)
        self.write(_REG_CONFIG, self.config)

    def getShuntVoltage_mV(self):
        self.write(_REG_CALIBRATION, self._cal_value)
        value = self.read(_REG_SHUNTVOLTAGE)
        if value > 32767:
            value -= 65535
        return value * 0.01

    def getBusVoltage_V(self):
        self.write(_REG_CALIBRATION, self._cal_value)
        self.read(_REG_BUSVOLTAGE)
        return (self.read(_REG_BUSVOLTAGE) >> 3) * 0.004

    def getCurrent_mA(self):
        value = self.read(_REG_CURRENT)
        if value > 32767:
            value -= 65535
        return value * self._current_lsb

    def getPower_W(self):
        self.write(_REG_CALIBRATION, self._cal_value)
        value = self.read(_REG_POWER)
        if value > 32767:
            value -= 65535
        return value * self._power_lsb

# ---------- Helpers & monitor ----------

def _sanitize(x):
    try:
        x = float(x)
        return x if math.isfinite(x) else None
    except Exception:
        return None

def make_ina219_read_fn(i2c_bus: int = 1, addr: int = 0x41) -> Callable[[], Tuple[Optional[float], Optional[float]]]:
    """
    Build a one-shot reader that returns (load_voltage_V, current_A).
    Defaults: i2c_bus=1, addr=0x41 to match your sample script.
    """
    sensor = INA219(i2c_bus=i2c_bus, addr=addr)
    def _read_once():
        v = sensor.getBusVoltage_V()           # Load-side voltage (V-)
        cur_mA = sensor.getCurrent_mA()        # mA (may be negative)
        v = _sanitize(v)
        a = _sanitize(cur_mA / 1000.0 if cur_mA is not None else None)
        if v is None or a is None:
            return (None, None)
        return (v, a)
    return _read_once

class UPSMonitor:
    """
    Polls read_fn() -> (volts, amps) at interval_s.
    Any failure or non-finite -> stores (None, None).
    """
    def __init__(self, read_fn, interval_s=0.5):
        self._read_fn = read_fn
        self._interval = float(interval_s)
        self._latest = (None, None)
        self._run = False
        self._thr = None

    def start(self):
        if self._thr:
            return
        self._run = True
        self._thr = threading.Thread(target=self._loop, daemon=True)
        self._thr.start()

    def _loop(self):
        while self._run:
            try:
                v, a = self._read_fn()
                v = _sanitize(v)
                a = _sanitize(a)
                self._latest = (None, None) if (v is None or a is None) else (v, a)
            except Exception:
                self._latest = (None, None)
            time.sleep(self._interval)

    def get(self) -> Tuple[Optional[float], Optional[float]]:
        return self._latest

    def stop(self):
        self._run = False
        if self._thr:
            self._thr.join(timeout=1.0)
        self._thr = None
