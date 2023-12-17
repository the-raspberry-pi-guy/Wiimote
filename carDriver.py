import numpy as np
import cwiid, time  # noqa: E401
import socket

print('Please press SYNC on your Wii board now ...')
time.sleep(1)

wiiBoard = None
wiiMote = None
# This code attempts to connect to your Wiimote and if it fails the program quits
while wiiBoard is None or wiiMote is None:
	try:
		wii=cwiid.Wiimote()
		wii.rpt_mode = cwiid.RPT_BALANCE
		time.sleep(0.1)
		if wii.state["ext_type"] == cwiid.EXT_BALANCE:
			wiiBoard = wii
			wii = None
			wiiBoard.rpt_mode = cwiid.RPT_BALANCE | cwiid.RPT_BTN
			wiiBoard.led = 1
			print("Board Connected")
		else:
			wiiMote = wii
			wii = None
			wiiMote.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_NUNCHUK
			wiiMote.led = cwiid.LED1_ON | cwiid.LED4_ON
			print("Wiimote connected")
	except RuntimeError:
		print("Cannot connect to your Wiimote or Wii Board. Run again and make sure you are holding buttons 1 + 2 (or SYNC)!")


try:
	wiiMote.state["nunchuk"]
except KeyError:
	print("Cannot connect to your Nunchuk. Make sure it is plugged in!")
	quit()
balance_calibration = wiiBoard.get_balance_cal()
named_calibration = { 
	'right_top': balance_calibration[0],
	'right_bottom': balance_calibration[1],
	'left_top': balance_calibration[2],
	'left_bottom': balance_calibration[3],
}
def connect_socket():
    connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    connection.settimeout(0.4)
    return connection


def get_vals() -> list:
	weights = []
	readings = wiiBoard.state["balance"]
	for sensor in ('right_top', 'right_bottom', 'left_top', 'left_bottom'):
		reading = readings[sensor]
		calibration = named_calibration[sensor]
		
		if reading > calibration[2]*2:
			print("Warning", sensor, "reading above upper calibration value")
		# 1700 appears to be the step the calibrations are against.
		# 17kg per sensor is 68kg, 1/2 of the advertised Japanese weight limit.
		if reading < calibration[1]:
			weights.append(1700 * (reading - calibration[0]) / (calibration[1] - calibration[0]))
		else:
			weights.append(1700 * (reading - calibration[1]) / (calibration[2] - calibration[1]) + 1700)
	return weights

def calcweight( readings, calibrations ) -> int: 
	"""
	Determine the weight of the user on the board in hundredths of a kilogram
	"""
	weight = 0
	for sensor in ('right_top', 'right_bottom', 'left_top', 'left_bottom'):
		reading = readings[sensor]
		calibration = calibrations[sensor]
	
		# 1700 appears to be the step the calibrations are against.
		# 17kg per sensor is 68kg, 1/2 of the advertised Japanese weight limit.
		if reading < calibration[1]:
			weight += 1700 * (reading - calibration[0]) / (calibration[1] - calibration[0])
		else:
			weight += 1700 * (reading - calibration[1]) / (calibration[2] - calibration[1]) + 1700

	return weight

def calculate_centroid(sensor_readings, sensor_positions):
	# Normalize sensor readings
	normalized_readings = sensor_readings / np.sum(sensor_readings)

	# Calculate relative positions
	relative_positions = np.dot(normalized_readings, sensor_positions)

	return relative_positions

def convert_relative_positions_to_coordinates(relative_positions, scaling_factor) -> list[int]:
	# Convert relative positions to coordinates
	coordinates = relative_positions * scaling_factor

	if round(((calcweight(wiiBoard.state['balance'], named_calibration) / 100.0)*2.205)-add, 1) > 35.0:
		return coordinates
	else:
		return [0,0]
	
def getStandardSpeed(coordinate:int, dif=20) -> int:
	if coordinate < 0:
		speed = (coordinate+dif)*100
		if speed < -4000:
			return 4000
		if speed > -2000:
			return 2000
		return -speed
	elif coordinate > 0:
		speed = (coordinate-dif)*100
		if speed > 4000:
			return 4000
		if speed < 2000:
			return 2000
		return speed
	else: 
		return 0
# Example usage
sensor_positions = np.array([[68, 68], [68, -68], [-68, 68], [-68, -68]])
scaling_factor = 1

connection = connect_socket()
"""
time.sleep(3)
print("Type anything to balance weight")
c = input()
add = (calcweight(wiiBoard.state['balance'], named_calibration) / 100.0)*2.205
print("Step On!")
time.sleep(3)"""
add = 0

try:
	while True:
		# Raw knowledge
		mote_state = wiiMote.state
		board_state = wiiBoard.state
		
		# Temporary knowledge
		centroid = calculate_centroid(get_vals(), sensor_positions)
		
		# Filtered knowledge
		coordinates = convert_relative_positions_to_coordinates(centroid, scaling_factor)
		weight = round(((calcweight(wiiBoard.state['balance'], named_calibration) / 100.0)*2.205)-add, 1)

		# Get direction
		x = 0
		y = 0

		if coordinates[0] >= 30:
			x = 1
		elif coordinates[0] <= -30:
			x = -1
		
		if coordinates[1] >= 30:
			y = 1
		elif coordinates[1] <= -30:
			y = -1

		moving = 0
		buttons = mote_state["buttons"]

		# Driving
		if mote_state["buttons"] == cwiid.BTN_B:
			connection.sendto(b"CMD_MOTOR#0#0#0#0", ("192.168.1.140", 4000))
			moving = 0
			time.sleep(0.2)
			continue
		
		if 3 != moving and ((buttons-cwiid.BTN_A) == cwiid.BTN_LEFT):
			connection.sendto(b"CMD_MOTOR#-500#-500#500#500", ("192.168.1.140", 4000))
			moving = 3


		elif 4 != moving and ((buttons-cwiid.BTN_A) == cwiid.BTN_RIGHT):
			connection.sendto(b"CMD_MOTOR#500#500#-500#-500", ("192.168.1.140", 4000))
			moving = 4

		elif 1 != moving and ((buttons-cwiid.BTN_A) == cwiid.BTN_UP):
			connection.sendto(b"CMD_MOTOR#1500#1500#1500#1500", ("192.168.1.140", 4000))
			moving = 1

		elif 2 != moving and ((buttons-cwiid.BTN_A) == cwiid.BTN_DOWN):
			connection.sendto(b"CMD_MOTOR#-1500#-1500#-1500#-1500", ("192.168.1.140", 4000))
			moving = 2
		
		elif buttons-cwiid.BTN_A == 0:
			connection.sendto(b"CMD_MOTOR#0#0#0#0", ("192.168.1.140", 4000))
			moving = 0




		

		elif x == 0 and y == 0 and 0 != moving:
			connection.sendto(b"CMD_MOTOR#0#0#0#0", ("192.168.1.140", 4000))
			moving = 0

		elif 1 != moving and y == 1:
			connection.sendto(b"CMD_MOTOR#1500#1500#1500#1500", ("192.168.1.140", 4000))
			moving = 1

		elif 2 != moving and y == -1:
			connection.sendto(b"CMD_MOTOR#-1500#-1500#-1500#-1500", ("192.168.1.140", 4000))
			moving = 2

		elif 3 != moving and x == -1:
			connection.sendto(b"CMD_MOTOR#-500#-500#500#500", ("192.168.1.140", 4000))
			moving = 3

		elif 4 != moving and x == 1:
			connection.sendto(b"CMD_MOTOR#500#500#-500#-500", ("192.168.1.140", 4000))
			moving = 4

		time.sleep(0.1)
except KeyboardInterrupt:
	wiiBoard.close()
	wiiMote.close()

