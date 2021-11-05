# MQTT-DS18B20
An MQTT-publishing DS18B20 temperature sensor utility for Raspberry Pi.

## Why?
MQTT is the preferred IoT data transmission protocol that follows a publisher-subscriber pattern. This is particularly handy for things like temperature sensors, because multiple sensors can easily be set up with minimal differences in configuration. Each sensor only needs:
- The address of the MQTT broker.
- A topic for the MQTT packets. (This is essentially the identifier for the sensor.)

## Setup
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

This will enable the 1-Wire bus on GPIO BCM pin 17, and enable GPIO BCM pin 27 to output a high signal. This allows the DS18B20 sensor (with a 4.7 kΩ resistor) to be plugged directly into a female GPIO header without the need for jumper wires. The intended use is to plug the component into the GPIO header with the negative, data, and positive pins on the physical GPIO pins 9, 11, and 13, respectively.

If you would prefer to use the default 1-Wire pin (BCM pin 4) and connect the positive pin on the DS18B20 component to a dedicated 3.3V pin instead, then you could simply add the following to `/boot/config.txt` instead:
```
dtoverlay=w1-gpio
```
Be sure to reboot the Raspberry Pi after making changes to the boot configuration file.

At this point, the DS18B20 sensor should be set up. Before proceeding, reading from the sensor can be tested by running `python3` to start the Python REPL interface, and executing the following:
```
import ds18b20
ds18b20.readTemperature ()
```
Assuming a numerical return value is printed to the Python REPL output, you should be good to go. If an error occurs, or `None` is returned, then there may be an issue with the wiring of the DS18B20 component, or the configuration of the 1-Wire bus.

## Configuration
The `.env.example` file included in the repository provides a template configuration file that can be used as a starting point. First, copy the file to the real configuration file:
```
cp .env.example .env
```
Then you can modify the new `.env` configuration file using your file editor of choice.

The example configuration file contains the following entries:
- `HOST` _(Required)_: The address of the broker, either as an IP address or a hostname.
- `PORT` _(Default: **1883**)_: The port on which the broker is running.
- `TOPIC` _(Default: **sensor/temperature**)_: The topic used in MQTT messages to the broker. This should be unique between different sensors if multiple sensors are used.
- `KEEPALIVE` _(Default: **60**)_: Maximum period in seconds allowed between communications with the broker. Also controls the period between "heartbeat" pings sent to the broker.
- `FORMAT` _(Default: **C**)_: The format used for the payload. The allowed values are:
   - `C` (Celsius)
   - `F` (Fahrenheit)
   - `K` (Kelvin)
- `PRECISION` _(Default: **3**)_: The number of decimal points to include in the payload temperature.
