# Air Monitoring HAT

## Pinout (Internally connected via header)

| Peripheral Pins  | Raspberry Pi Pins |
| ---------------- | ----------------- |
| 5V     	| 5V       |
| GND     	| GND      |
| PMS RX    | GPIO14   |
| PMS TX    | GPIO15   |
| PMS SET   | GPIO27   |
| PMS RESET | GPIO17   |
| Oled SDA  | GPIO2    |
| Oled SCL  | GPIO3    |


### Enable I2C and Serial Interface

Open a terminal and run the following commands to enable I2C and Serial：


``` sudo raspi-config ```

Choose Interfacing Options -> I2C ->yes 


``` sudo raspi-config ```

Choose Interfacing Options -> Serial -> No -> Yes


## Testing

### Clone Repository

``` git clone https://github.com/sbcshop/Air-Monitoring-HAT.git ```
``` cd Air-Monitoring-HAT ```

Run GUI by running below command:

``` python3 Air_monitoring_GUI.py ```

Select <b>COM port</b> from above GUI ("/dev/ttyS0" in case of default connection), 
and click on the start button to start Real-Time data from the sensor.



