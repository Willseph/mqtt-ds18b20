# mqtt-ds18b20

## Installation
First, configure `/boot/config.txt` by adding the following lines:
```
dtoverlay=w1-gpio,gpiopin=17
dtoverlay=gpio-poweroff,gpiopin=27,active_low
```

This will enable the 1-Wire bus on GPIO BCM pin 17, and enable GPIO BCM pin 27 to output a high signal. Doing this will allow a DS18B20 sensor (with a 4.7 kΩ resistor) to be plugged directly into a female GPIO header without the need for jumper wires. The intended use is to plug the component into the GPIO header with the negative, data, and positive pins on the physical GPIO pins 9, 11, and 13, respectively.
