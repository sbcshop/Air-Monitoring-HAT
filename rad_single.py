#!/usr/bin/env python3

# Script to Read and Display the Results of a Check
# Designed to be put in a cron

import argparse
import logging
import json
from os import path

from pms_a003 import Sensor
from oled_091 import SSD1306
from time import sleep
from serial import SerialException

DIR_PATH = path.abspath(path.dirname(__file__))
DefaultFont = path.join(DIR_PATH, "Fonts/GothamLight.ttf")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--verbose", action="append_const", help="Verbosity Controls",
                        const=1, default=[])

    parser.add_argument("-j", "--json", help="JSON, Write Out", default=None)

    args = parser.parse_args()

    VERBOSE = len(args.verbose)

    if VERBOSE == 0:
        logging.basicConfig(level=logging.ERROR)
    elif VERBOSE == 1:
        logging.basicConfig(level=logging.WARNING)
    elif VERBOSE == 2:
        logging.basicConfig(level=logging.INFO)
    elif VERBOSE > 2:
        logging.basicConfig(level=logging.DEBUG)

    logger = logging.getLogger("rad_single.py")

    # Initalize Sensor
    oled_display = SSD1306()
    air_mon = Sensor()
    air_mon.connect_hat(port="/dev/ttyS0", baudrate=9600)


def info_print():
    oled_display.DirImage(path.join(DIR_PATH, "Images/SB.png"))
    oled_display.DrawRect()
    oled_display.ShowImage()
    sleep(1)
    oled_display.PrintText("  Waiting....", FontSize=14)
    oled_display.ShowImage()

    try:
        values = air_mon.read()

        jsonic_data = dict(pm1_0=values.pm10_cf1,
                           pm2_5=values.pm25_cf1,
                           pm10=values.pm100_cf1)


        oled_display.PrintText("PM1.0= {:2d}".format(values.pm10_cf1),
                               cords=(2, 2), FontSize=10)
        oled_display.PrintText("PM2.5= {:2d}".format(values.pm25_cf1),
                               cords=(65, 2), FontSize=10)
        oled_display.PrintText("PM10= {:2d}".format(values.pm100_cf1),
                               cords=(25, 20), FontSize=13)
        oled_display.ShowImage()

    except KeyboardInterrupt:
        air_mon.disconnect_hat()
    else:

        if args.json:
            logger.debug("Implement Write Out Feature Set.")

        logger.debug(json.dumps(jsonic_data))

