import os
import glob


def read_temp_raw ():
	os.system('sudo modprobe w1-gpio')
	os.system('sudo modprobe w1-therm')
	base_dir = '/sys/bus/w1/devices/'
	device_file = None
	device_folders = glob.glob(base_dir + '28*')

	if len(device_folders) > 0:
		device_folder = device_folders[0]
		device_file = device_folder + '/w1_slave'

	if (not device_file):
		return None
	f = open(device_file, 'r')
	lines = f.readlines()
	f.close()
	return lines


def readTemperature ():
	lines = read_temp_raw()
	if (not lines):
		return None
	if len(lines) >= 2 and 'YES' in lines[0] and 't=' in lines[1]:
		return int(lines[1].split('t=', 1)[1].strip())
	return None
