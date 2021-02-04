#!/usr/bin/python3
"""
Display live sensor values.
"""
import pms_a003
from oled_091 import SSD1306


class AirReader(object):
    def __init__(self):
        self.sensor = None
        self.display = None
        self.alive = None

        self.var_pm_1 = 0
        self.var_pm_10 = 0
        self.var_pm_2_5 = 0

        self.display = SSD1306()

    def connect(self, port="/dev/ttyS0", baudrate=9600):
        try:
            self.sensor = pms_a003.Sensor()
            self.sensor.connect_hat(port, baudrate)
            self.alive = True
        except:
            self.alive = False

    def disconnect(self):
        if self.alive:
            self.sensor.disconnect_hat()

    def read_value(self):
        """Read a sensor value and store it in the database."""
        # Read the value from the sensor.
        reading = self.sensor.read()
        self.var_pm_1 = reading.pm10_cf1
        self.var_pm_2_5 = reading.pm25_cf1
        self.var_pm_10 = reading.pm100_cf1

    def print_to_oled(self):
        self.display.PrintText("PM1.0= {:2d}".format(self.var_pm_1),
                               cords=(2, 2), FontSize=10)
        self.display.PrintText("PM2.5= {:2d}".format(self.var_pm_2_5),
                               cords=(65, 2), FontSize=10)
        self.display.PrintText("PM10= {:2d}".format(self.var_pm_10),
                               cords=(25, 20), FontSize=13)
        self.display.ShowImage()

    def update_data(self):
        self.read_value()
        self.print_to_oled()
        return self.var_pm_1, self.var_pm_2_5, self.var_pm_10
