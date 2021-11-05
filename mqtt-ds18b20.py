#!/usr/bin/python3

# IMPORTS
from dotenv import dotenv_values
from ds18b20 import readTemperature
import json
import paho.mqtt.client as mqtt


# CONSTS
CONFIG_HOST = "HOST"
CONFIG_PORT = "PORT"
CONFIG_TOPIC = "TOPIC"
CONFIG_KEEPALIVE = "KEEPALIVE"
CONFIG_FORMAT = "FORMAT"
CONFIG_PRECISION = "PRECISION"
CONFIG_LOOP_DELAY = "LOOP_DELAY"
HOST_PLACEHOLDER = "X.X.X.X"
FORMATS = ["C", "F", "K"]


# FUNCTIONS
def verifyConfigPropertyString (config, key, validValues=None):
	if not key in config or not config[key]:
		print("Missing config value: %s" % (key))
		return False
	if validValues and not config[key] in validValues:
		print("Invalid config value: %s" % (key))
		print("Value must be one of: %s" % (json.dumps(validValues)))
		return False
	return True

def verifyConfigPropertyInt (config, key, minimum=0):
	if not key in config or not config[key]:
		print("Missing config value: %s" % (key))
		return False
	if not config[key].isdigit():
		print("Invalid numerical config value: %s" % (key))
		return False
	if int(config[key]) < minimum:
		print("Invalid numerical config value: %s" % (key))
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

	# Checking PORT
	valid = valid and verifyConfigPropertyInt (config, CONFIG_PORT)
	valid = valid and verifyConfigPropertyString (config, CONFIG_TOPIC)
	valid = valid and verifyConfigPropertyInt (config, CONFIG_KEEPALIVE, 1)
	valid = valid and verifyConfigPropertyString (config, CONFIG_FORMAT, FORMATS)
	valid = valid and verifyConfigPropertyInt (config, CONFIG_PRECISION)
	valid = valid and verifyConfigPropertyInt (config, CONFIG_LOOP_DELAY)

	return valid


# MAIN
def main():
	config = dotenv_values(".env")
	if not verifyConfig(config):
		print("Error with configuration. Check logs and README.md file for issues.")
		return

	print("Configuration loaded.")

if __name__ == "__main__":
	main()
