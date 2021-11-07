# MQTT-DS18B20
An MQTT-publishing DS18B20 temperature sensor utility for Raspberry Pi.

## Why?
MQTT is the preferred IoT data transmission protocol that follows a publisher-subscriber pattern. This is particularly handy for things like temperature sensors, because multiple sensors can easily be set up with minimal differences in configuration. Each sensor only needs:
- The address of the MQTT broker.
- A topic for the MQTT packets. (This is essentially the identifier for the sensor.)

To see an example of the data sent to the broker, scroll down to the [Example Data](#Example%20Data) section further down.

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
pip3 install paho-mqtt python-dotenv
```

Also, because of the way `pip3` works, you may also need to install the dependencies in a **sudo** context as well in order for the service to run later on:
```
sudo pip3 install paho-mqtt python-dotenv
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
- `TOPIC_ROOT` _(Default: **sensor/temperature**)_: The root-level topic used in MQTT messages to the broker. This should be unique between different sensors if multiple sensors are used.
- `TOPIC_READING` _(Default: **${TOPIC_ROOT}/reading**)_: The subtopic used for temperature reading messages sent to the broker.
- `TOPIC_STATUS` _(Default: **${TOPIC_ROOT}/status**)_: The subtopic used for status messages sent to the broker.
- `KEEPALIVE` _(Default: **60**)_: Maximum period in seconds allowed between communications with the broker. Also controls the period between "heartbeat" pings sent to the broker.
- `FORMAT` _(Default: **C**)_: The format used for the payload. The allowed values are:
   - `C` (Celsius)
   - `F` (Fahrenheit)
   - `K` (Kelvin)
- `PRECISION` _(Default: **3**)_: The number of decimal points to include in the payload temperature.
- `LOOP_DELAY` _(Default: **10**)_: The delay, in seconds, between sensor readings and MQTT messages published to the broker.
   - Note: Using the value **0** will read from the sensor and publish updates to the broker as frequently as possible.
- `STATUS_CONNECTED` _(Default: **connected**)_: The payload included in the status update sent after connecting to the broker.
- `STATUS_DISCONNECTED` _(Default: **disconnected**)_: The payload included in the status update sent after connecting to the broker.
- `STATUS_LWT` _(Default: **gone**)_: The payload included in the "last will" message sent to the broker prior to connection.

## Service
After configuring the settings in the `.env` file, the service can finally be enabled. Beforehand, it's recommended that you manually test the script first by running it as-is:
```
./mqtt-ds18b20.py
```
Assuming the output looks something like this:
```
Configuration loaded.
Checking for DS18B20 sensor...
Sensor read successful.
Connecting to MQTT broker at _hostname_:_port_
Client connected.
Beginning sensor reading and publish loop...
```
You can safely assume that the script is correctly configured and running normally. If the script exits right away with some kind of error or stack trace, then you may need to verify your configuration file or wiring.

This repository contains an example systemd unit file that can be copied over to the proper directory, with only a small change required.

First, copy the unit file example to the final location. In most cases, that will be the `/etc/systemd/system` directory:
```
sudo cp mqtt-ds18b20.service.example /etc/systemd/system/mqtt-ds18b20.service
```

From there, you can modify the new `mqtt-ds18b20.service` file. You'll need to modify the following line to replace the example absolute path to the cloned repo:
```
ExecStart=/path/to/repo/mqtt-ds18b20/mqtt-ds18b20.py
```

Finally, with the service unit file added, it can be enabled to start automatically after a reboot:
```
sudo systemctl enable mqtt-ds18b20
```
You can either reboot the Raspberry Pi to start the service and begin publishing the temperature readings to the MQTT broker, or the service can be started manually without rebooting:
```
sudo systemctl start mqtt-ds18b20
```

## Example Data
In order to verify that the service is working correctly, subscribers will need to be set up on the two topics used by the service. The topics, subtopics, and payload formats are entirely customizable in the configuration file.

As a basic example, using the default values provided in the `.env.example` configuration, you can expect to see messages like:
```
connected
17.750
17.875
17.812
...
```
These can be seen by subscribing to the wildcard topic `sensor/temperature/+`.

The two topics used in messages sent to the broker are (by default):
- `reading`: Used for the actual temperature readings from the DS18B20 sensor. By default, the values are in Celsius, rounded to three decimal places.
- `status`: Used for status messages, when the client connects or disconnects from the broker, as well as the "last will and testament" message.

When the script starts and first connects to the MQTT broker, the initial `connected` payload message with the `sensor/temperature/status` topic will be sent before any temperature readings.

If the service is manually stopped, or otherwise a non-MQTT related issue occurs (such as an issue occurring with the DS18B20 sensor), the script will attempt to send a final `disconnected` payload message before disconnecting the client. However, prior to the client connecting to the broker, a "last will and testament" message is sent to the broker with the payload `gone`. This message will be sent by the broker to all subscribers if the broker has not received any messages from the service after a period of time.
