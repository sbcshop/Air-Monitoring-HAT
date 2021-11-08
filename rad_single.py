#!/usr/bin/env python3

# Script to Read and Display the Results of a Check
# Designed to be put in a cron

import argparse
import logging
import json
import time
from os import path

import pms_a003
from pms_a003 import Sensor
from oled_091 import SSD1306
from time import sleep
from serial import SerialException

DIR_PATH = path.abspath(path.dirname(__file__))
DefaultFont = path.join(DIR_PATH, "Fonts/GothamLight.ttf")

def collect_data(max=5):
    air_mon = Sensor()
    air_mon.connect_hat(port="/dev/ttyS0", baudrate=9600)

    values = None

    for x in range(0, max):
        if x > 0:
            logger.debug("Retrying Attempt {}".format(x))
            time.sleep(3)

        try:
            values = air_mon.read()
        except SerialException as se:
            logger.warning("Serial Exception found when requesting Data: {}".format(se))
        except pms_a003.SensorException as sensor_exception:
            logger.warning("Sensor Exception : {}".format(sensor_exception))
        except Exception as gen_err:
            logger.warning("General Error: {} {}".format(type(gen_err), gen_err))
            break
        else:
            # It worked Break Out
            break

    air_mon.disconnect_hat()

    return values



def info_print(oled_display, ari_mon):
    oled_display.DirImage(path.join(DIR_PATH, "Images/SB.png"))
    oled_display.DrawRect()
    oled_display.ShowImage()
    sleep(1)
    oled_display.PrintText("  Waiting....", FontSize=14)
    oled_display.ShowImage()

    info = dict(okay=False, data={})

    try:
        values = collect_data()

        jsonic_data = dict(pm1_0=values.pm10_cf1,
                           pm2_5=values.pm25_cf1,
                           pm10=values.pm100_cf1)

        logger.debug(jsonic_data)

        oled_display.PrintText("PM1.0= {:2d}".format(values.pm10_cf1),
                               cords=(2, 2), FontSize=10)
        oled_display.PrintText("PM2.5= {:2d}".format(values.pm25_cf1),
                               cords=(65, 2), FontSize=10)
        oled_display.PrintText("PM10= {:2d}".format(values.pm100_cf1),
                               cords=(25, 20), FontSize=13)
        oled_display.ShowImage()

    except Exception as e:
        logger.warning("Error Reading From Sensor : {}".format(e))
        info["okay"] = False

    else:

        if args.json:
            logger.debug("Implement Write Out Feature Set.")

        logger.debug(json.dumps(jsonic_data))
        info["okay"] = True
        info["data"] = jsonic_data

    return info

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--verbose", action="append_const", help="Verbosity Controls",
                        const=1, default=[])

    parser.add_argument("-j", "--json", help="JSON, Write Out", default=None)
    parser.add_argument("-n", "--nrpe", help="NRPE Write out", default=False, action="store_true")

    args = parser.parse_args()

    VERBOSE = len(args.verbose)

    if VERBOSE == 0 or args.nrpe is True:
        logging.basicConfig(level=logging.ERROR)
    elif VERBOSE == 1:
        logging.basicConfig(level=logging.WARNING)
    elif VERBOSE == 2:
        logging.basicConfig(level=logging.INFO)
    elif VERBOSE > 2:
        logging.basicConfig(level=logging.DEBUG)

    logger = logging.getLogger("rad_single.py")
    logger.info("Running rad_single.py")

    # Initalize Sensor
    oled_display = SSD1306()
    #air_mon = Sensor()
    #air_mon.connect_hat(port="/dev/ttyS0", baudrate=9600)

    info = info_print(oled_display)


