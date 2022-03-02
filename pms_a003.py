import serial
import time
import json
import logging


class PMSReading(object):
    """One single reading."""

    def __init__(self, line):
        self.logger = logging.getLogger("PMSReading")
        self.logger.debug(line)

        #
        # Docs Found Here: https://github.com/adafruit/Adafruit_CircuitPython_PM25/blob/main/adafruit_pm25/__init__.py#L53
        #

        self.pm10_cf1 = line[4] * 256 + line[5] # PM1.0 μm/m^3 Standard Atmosphere
        self.pm25_cf1 = line[6] * 256 + line[7] # PM2.5 μm/m^3 Standard Atmosphere
        self.pm100_cf1 = line[8] * 256 + line[9] # PM10.0 μm/m^3 Standard Atmosphere
        self.pm10_std = line[10] * 256 + line[11] # PM1.0 μm/m^3 Current Atmosphere
        self.pm25_std = line[12] * 256 + line[13] # PM2.5 μm/m^3 Current Atmosphere
        self.pm100_std = line[14] * 256 + line[15] # PM10.0 μm/m^3 Current Atmosphere
        self.gr03um = line[16] * 256 + line[17] # Particles > 0.3 μm per 0.1L air
        self.gr05um = line[18] * 256 + line[19] # Particles > 0.5 μm per 0.1L air
        self.gr10um = line[20] * 256 + line[21] # Particles > 1.0 μm per 0.1L air
        self.gr25um = line[22] * 256 + line[23] # Particles > 2.5 μm per 0.1L air
        self.gr50um = line[24] * 256 + line[25] # Particles > 5.0 μm per 0.1L air
        self.gr100um = line[26] * 256 + line[27] # Particles > 10 μm per 0.1L air



class SensorException(Exception):
    """Exception if no data can be read."""
    pass


class Sensor(object):
    """The interface class."""

    def __init__(self):
        self.ser = None
        self.read_timeout = 1

    def connect_hat(self, port="/dev/ttyS0", baudrate=9600, read_timeout=1):
        self.read_timeout = read_timeout
        try:
            self.ser = serial.Serial(port=port, baudrate=baudrate,
                                     timeout=read_timeout)
        except serial.SerialException as e:
            raise SensorException(str(e))

    def disconnect_hat(self):
        if self.ser:
            self.ser.close()

    @staticmethod
    def _verify(rec):
        """Verify the checksum of the data."""
        calc = 0
        ord_arr = []
        for c in bytearray(rec[:-2]):
            calc += c
            ord_arr.append(c)
        sent = (rec[-2] << 8) | rec[-1]
        if sent != calc:
            raise SensorException("Checksum invalid")

    def read(self):
        """Read a new value from the sensor."""
        rec = b''
        timeout_time = time.monotonic() + self.read_timeout
        self.ser.reset_input_buffer()
        while True:
            inp = self.ser.read(1)
            if inp == '':
                time.sleep(0.1)
                continue
            if inp == b'\x42':
                rec += inp
                inp = self.ser.read(1)
                if inp == b'\x4d':
                    rec += inp
                    rec += self.ser.read(30)
                    break
            if time.monotonic() > timeout_time:
                raise SensorException("No message received")
        self._verify(rec)
        return PMSReading(rec)
