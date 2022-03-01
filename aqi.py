#!/usr/bin/env python3

import math
import logging

#
# Attempt to Caluculate AQI from Data
# https://forum.airnowtech.org/t/the-aqi-equation/169
#

def f_estimateAQI(collection):

    logger = logging.getLogger("f_estimateAQI")

    _pm25_table = {"Good": {"cl": 0.0, "ch": 12.0,
                            "aqil": 0, "aqih": 50},
                   "Moderate": {"cl": 12.1, "ch": 35.4,
                                "aqil": 51, "aqih": 100},
                   "Unhealthy for Sensitive Groups": {"cl": 35.5, "ch": 55.4,
                                                      "aqil": 101, "aqih": 150},
                   "Unhealthy": {"cl": 55.5, "ch": 150.4,
                                 "aqil": 150.5, "aqih": 250.4},
                   "Very Unhealthy": {"cl": 150.5, "ch": 250.4,
                                      "aqil": 201, "aqih": 300},
                   "Hazardous": {"cl": 250.5, "ch": 500.4,
                                 "aqil": 301, "aqih": 500}}

    pm25_rounded = math.ceil(collection.pm25_cf1 * 10) / 10

    eaqi = None
    eaqi_honorrific = None

    if pm25_rounded >= 500.5:
        eaqi = 501
        eaqi_honorrific = "Ludicrous"

    for honorrific, table in _pm25_table.items():

        if pm25_rounded >= table["cl"] and pm25_rounded < table["ch"]:
            # use
            eaqi_honorrific = honorrific

            left = (table["aqilh"] - table["aquil"]) / (table["ch"] - table["cl"])
            right = ((pm25_rounded - table["cl"]))
            eaqi = left * right + table["aqil"]

            break
        else:
            continue

    return eaqi, eaqi_honorrific


