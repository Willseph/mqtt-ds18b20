# MQTT-DS18B20
An MQTT-publishing DS18B20 temperature sensor utility for Raspberry Pi.

## Why?
MQTT is the preferred IoT data transmission protocol that 

## Installation
If not already done so, make sure `git` is installed prior to cloning this repository:
```
sudo apt-get install git
```
After that, the repository can be cloned using the link above.

This project is based in Python 3, and some dependencies are required to be installed via `pip3`. If necessary, `pip3` can be installed using `apt-get`:
```
sudo apt-get install python3-pip
```

From there, use the `pip3` command to install the necessary dependencies:
```
pip3 install paho-mqtt
```

It is also required that you enable the 1-Wire interface in order to read from the DS18B20 sensor. Personally, I recommend configuring `/boot/config.txt` by adding the following lines:
```
dtoverlay=w1-gpio,gpiopin=17
dtoverlay=gpio-poweroff,gpiopin=27,active_low
```

This will enable the 1-Wire bus on GPIO BCM pin 17, and enable GPIO BCM pin 27 to output a high signal. Doing this will allow a DS18B20 sensor (with a 4.7 kΩ resistor) to be plugged directly into a female GPIO header without the need for jumper wires. The intended use is to plug the component into the GPIO header with the negative, data, and positive pins on the physical GPIO pins 9, 11, and 13, respectively.

If you would prefer to use the default 1-Wire pin (BCM pin 4) and connect the positive pin on the DS18B20 component to a dedicated 3.3V pin instead, then you could simply add the following to `/boot/config.txt` instead:
```
dtoverlay=w1-gpio
```
