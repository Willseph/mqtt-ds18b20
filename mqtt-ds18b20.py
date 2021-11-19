#!/usr/bin/python3

# IMPORTS
from dotenv import dotenv_values
from ds18b20 import readTemperature
import json
import os
import paho.mqtt.client as mqtt
import signal
import sys
import time
import traceback


# CONSTS
CONFIG_HOST = "HOST"
CONFIG_PORT = "PORT"
CONFIG_TOPIC_READING = "TOPIC_READING"
CONFIG_TOPIC_STATUS = "TOPIC_STATUS"
CONFIG_KEEPALIVE = "KEEPALIVE"
CONFIG_FORMAT = "FORMAT"
CONFIG_PRECISION = "PRECISION"
CONFIG_LOOP_DELAY = "LOOP_DELAY"
CONFIG_STATUS_CONNECTED = "STATUS_CONNECTED"
CONFIG_STATUS_DISCONNECTED = "STATUS_DISCONNECTED"
CONFIG_STATUS_LWT = "STATUS_LWT"
HOST_PLACEHOLDER = "X.X.X.X"
FORMATS = ["C", "F", "K"]
CONN_FAIL_SLEEP = 5


# GLOBALS
signalKilled = False


# FUNCTIONS
def scriptDir():
	return os.path.dirname(os.path.realpath(__file__))

def handleSignalKilled(signum, frame):
	global signalKilled
	signalKilled = True

def verifyConfigPropertyString (config, key, validValues=None):
	if not key in config or not config[key]:
		print("Missing config value: %s" % (key))
		return False
	if validValues and not config[key] in validValues:
		print("Invalid config value: %s" % (key))
		print("Value must be one of: %s" % (json.dumps(validValues)))
		return False
	return True

def verifyConfigPropertyFloat (config, key, minimum=0):
	if not key in config or not config[key]:
		print("Missing config value: %s" % (key))
		return False
	val = None
	try:
		val = float(config[key])
	except:
		print("Invalid float config value: %s" % (key))
		return False
	if val < minimum:
		print("Invalid float config value: %s" % (key))
		print("Value must be greater than or equal to: %d" % (minimum))
		return False
	return True

def verifyConfigPropertyInt (config, key, minimum=0):
	if not key in config or not config[key]:
		print("Missing config value: %s" % (key))
		return False
	if not config[key].isdigit():
		print("Invalid integer config value: %s" % (key))
		return False
	if int(config[key]) < minimum:
		print("Invalid integer config value: %s" % (key))
		print("Value must be greater than or equal to: %d" % (minimum))
		return False
	return True


def verifyConfig (config):
	"""Checks the loaded configuration dictionary for invalid or missing values."""
	if not config:
		print("Could not load configuration file.")
		return False

	valid = True

	# Checking HOST
	valid = valid and verifyConfigPropertyString (config, CONFIG_HOST)
	if config[CONFIG_HOST] == HOST_PLACEHOLDER:
		print("%s value in configuration file not set." % (CONFIG_HOST))
		print("Replace the existing placeholder value with your MQTT broker address or hostname.")
		valid = False

	valid = valid and verifyConfigPropertyInt (config, CONFIG_PORT)
	valid = valid and verifyConfigPropertyString (config, CONFIG_TOPIC_READING)
	valid = valid and verifyConfigPropertyString (config, CONFIG_TOPIC_STATUS)
	valid = valid and verifyConfigPropertyFloat (config, CONFIG_KEEPALIVE, 1)
	valid = valid and verifyConfigPropertyString (config, CONFIG_FORMAT, FORMATS)
	valid = valid and verifyConfigPropertyInt (config, CONFIG_PRECISION)
	valid = valid and verifyConfigPropertyFloat (config, CONFIG_LOOP_DELAY)
	valid = valid and verifyConfigPropertyString (config, CONFIG_STATUS_CONNECTED)
	valid = valid and verifyConfigPropertyString (config, CONFIG_STATUS_DISCONNECTED)
	valid = valid and verifyConfigPropertyString (config, CONFIG_STATUS_LWT)

	return valid

def CtoF(celsius):
	return (celsius * (9.0/5.0)) + 32

def CtoK(celsius):
	return celsius + 273.15

def formatTemperature(rawTemp, format, precision):
	celsius = rawTemp/1000.0
	temp = None
	if format == 'C':
		temp = celsius
	elif format == 'F':
		temp = CtoF(celsius)
	elif format == 'K':
		temp = CtoK(celsius)
	else:
		raise ValueError("Invalid temperature format.")
	return ("{:.%df}" % (precision)).format(temp)

def getFormattedTemperature(client, config):
	rawTemp = readTemperature()
	if not rawTemp:
		raise ValueError("Unable to read from DS18B20 temperature sensor.")
	format = config[CONFIG_FORMAT]
	precision = int(config[CONFIG_PRECISION])
	return formatTemperature(rawTemp, format, precision)

def readFromSensorAndPublish(client, config):
	formattedTemp = getFormattedTemperature(client, config)
	if not formattedTemp:
		raise ValueError("Could not get temperature.")
	topic = config[CONFIG_TOPIC_READING]
	payload = formattedTemp
	print("Publishing: %s %s" % (topic, payload))
	client.publish(topic, payload, retain=True)

def beginSensorPublishLoop (client, config):
	"""Begins the actual loop to read from the sensor, and publish the reading to the MQTT broker."""
	global signalKilled
	loopDelay = float(config[CONFIG_LOOP_DELAY])
	while True:
		if signalKilled:
			raise ValueError("Detected sigkill, stopping script.")
		readFromSensorAndPublish(client, config)
		time.sleep(loopDelay)


def handleDisconnection(client, userdata, rc):
	global signalKilled
	signalKilled = True


# MAIN
def main():
	config = dotenv_values(os.path.join(scriptDir(), ".env"))
	if not verifyConfig(config):
		print("Error with configuration. Check logs and README.md file for issues.")
		return

	print("Configuration loaded.")
	print("Checking for DS18B20 sensor...")
	temp = readTemperature()
	if not temp:
		print("Could not read temperature from DS18B20 on 1-Wire interface.")
		return
	print("Sensor read successful.")

	statusTopic = config[CONFIG_TOPIC_STATUS]
	client = mqtt.Client()
	client.will_set(statusTopic, config[CONFIG_STATUS_LWT], retain=True)
	client.on_disconnect = handleDisconnection
	try:
		host = config[CONFIG_HOST]
		port = int(config[CONFIG_PORT])
		keepalive = int(config[CONFIG_KEEPALIVE])
		print("Connecting to MQTT broker at %s:%s" % (host, port))
		client.connect(host, port, keepalive)
	except KeyboardInterrupt:
		print("User cancelled.")
		return
	except:
		print("Could not connect to MQTT broker:")
		traceback.print_exc()
		print("Waiting %d seconds..." % (CONN_FAIL_SLEEP))
		time.sleep(CONN_FAIL_SLEEP)
		sys.exit(1)
		return

	print("Client connected.")
	client.publish(statusTopic, config[CONFIG_STATUS_CONNECTED], retain=True)

	signal.signal(signal.SIGINT, handleSignalKilled)
	signal.signal(signal.SIGTERM, handleSignalKilled)

	print("Beginning sensor reading and publish loop...")
	error = False
	try:
		beginSensorPublishLoop(client, config)
	except KeyboardInterrupt:
		print("User cancelled.")
	except:
		error = True
		traceback.print_exc()
	finally:
		print("Disconnecting client...")
		client.publish(statusTopic, config[CONFIG_STATUS_DISCONNECTED], retain=True)
		client.disconnect()
		if error:
			sys.exit(1)

if __name__ == "__main__":
	main()
