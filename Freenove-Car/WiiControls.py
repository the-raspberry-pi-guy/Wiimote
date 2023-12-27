from abc import ABCMeta
import numpy as np
import cwiid, time

def connect_multiple(devices: list) -> list:
	"""
	This connects multiple Wii devices in any order.
	The device list must with the cwiid EXT_TYPE you want to connect to.
	"""
	print('Please press SYNC on your device now ...')
	time.sleep(1) # wait for SYNC to be pressed

	found_devices = [] # to hold the classes with the wii device
	
	while len(found_devices) != len(devices): # loop until all are found
		try:
			wii=cwiid.Wiimote() # connect a remote
			time.sleep(0.1)
			if wii.state["ext_type"] == devices[len(found_devices)]:
				if devices[len(found_devices)] == cwiid.EXT_BALANCE:
					found_devices.append(Board(wii))
				else:
					found_devices.append(Remote(wii))

		except RuntimeError:
			print("Cannot connect to your Wiimote or Wii Board. Run again and make sure you are holding buttons 1 + 2 (or SYNC)!")
	return found_devices


class Board:
	"""
	For connecting to and interacting with a Wii Board
	"""

	def __init__(self, cwiid_device) -> None:
		self.device = cwiid_device
		self.device.rpt_mode = cwiid.RPT_BALANCE | cwiid.RPT_BTN
		self.device.led = 1
		self.ready = False
		print("Board Connected")

	def calc_weight(self, readings) -> int: 
		"""
		Determine the weight of the user on the board in hundredths of a kilogram
		"""
		weight = 0
		for sensor in ('right_top', 'right_bottom', 'left_top', 'left_bottom'):
			reading = readings[sensor]
			calibration = self.named_calibration[sensor]
		
			# 1700 appears to be the step the calibrations are against.
			# 17kg per sensor is 68kg, 1/2 of the advertised Japanese weight limit.
			if reading < calibration[1]:
				weight += 1700 * (reading - calibration[0]) / (calibration[1] - calibration[0])
			else:
				weight += 1700 * (reading - calibration[1]) / (calibration[2] - calibration[1]) + 1700

		return weight
	
	def _calculate_centroid(self, sensor_readings, ):
		sensor_positions = np.array([[68, 68], [68, -68], [-68, 68], [-68, -68]])
		# Normalize sensor readings
		normalized_readings = sensor_readings / np.sum(sensor_readings)

		# Calculate relative positions
		relative_positions = np.dot(normalized_readings, sensor_positions)

		return relative_positions

	def _convert_relative_positions_to_coordinates(self, relative_positions) -> list[int]:
		# Convert relative positions to coordinates (pointless now)
		coordinates = relative_positions

		if round(((self.calc_weight(self.device.state['balance'], self.named_calibration) / 100.0)*2.205)-self.weight_offset, 1) > 35.0:
			return coordinates
		else:
			return [0,0]
		
	def prepare(self) -> None:
		self.balance_calibration = self.device.get_balance_cal()
		self.named_calibration = { 
			'right_top': self.balance_calibration[0],
			'right_bottom': self.balance_calibration[1],
			'left_top': self.balance_calibration[2],
			'left_bottom': self.balance_calibration[3],
		}
		input("Step off!\n and enter something to balance weight: ")
		self.weight_offset = (self.calc_weight(self.device.state['balance'], self.named_calibration) / 100.0)*2.205
		print("Step On!")
		self.ready = True
					


class Remote:
	def __init__(self, cwiid_device) -> None:
		self.device = cwiid_device
		self.device.rpt_mode = cwiid.RPT_BTN
		self.device.led = cwiid.LED1_ON | cwiid.LED4_ON
		print("Wiimote Connected")
		print("External type =", self.device.state["ext_type"])
