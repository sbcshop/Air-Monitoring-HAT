from pms_a003 import Sensor


air_mon = Sensor()
air_mon.connect_hat(port="/dev/ttyS0", baudrate=9600)

values = air_mon.read()
print("PMS 1 value is {}".format(values.pm10_cf1))
print("PMS 2.5 value is {}".format(values.pm25_cf1))
print("PMS 10 value is {}".format(values.pm100_cf1))

air_mon.disconnect_hat()
