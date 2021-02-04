from pms_a003 import Sensor
from oled_091 import SSD1306
from time import sleep

oled_display = SSD1306()
air_mon = Sensor()
air_mon.connect_hat(port="/dev/ttyS0", baudrate=9600)

try:
    while True:
        values = air_mon.read()
        print("PM 1.0 : {} \tPM 2.5 : {} \tPM 10 : {}".format(
            values.pm10_cf1, values.pm25_cf1, values.pm100_cf1))

        oled_display.PrintText("PM1.0= {:2d}".format(values.pm10_cf1),
                               cords=(2, 2), FontSize=10)
        oled_display.PrintText("PM2.5= {:2d}".format(values.pm25_cf1),
                               cords=(65, 2), FontSize=10)
        oled_display.PrintText("PM10= {:2d}".format(values.pm100_cf1),
                               cords=(25, 20), FontSize=13)
        oled_display.ShowImage()
        sleep(1)

except KeyboardInterrupt:
    air_mon.disconnect_hat()

