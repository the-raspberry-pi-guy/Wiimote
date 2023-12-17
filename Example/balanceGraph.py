import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
import cwiid, time  # noqa: E401

button_delay = 0.5
TOP_RIGHT               = 0
BOTTOM_RIGHT            = 1
TOP_LEFT                = 2
BOTTOM_LEFT             = 3

style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

print('Please press buttons 1 + 2 on your Wiimote now ...')
time.sleep(1)

# This code attempts to connect to your Wiimote and if it fails the program quits
try:
  wii=cwiid.Wiimote()
except RuntimeError:
  print("Cannot connect to your Wiimote. Run again and make sure you are holding buttons 1 + 2!")
  quit()
wii.rpt_mode = cwiid.RPT_BALANCE
"""
b2i = lambda b: int(b.encode("hex"), 16)  # noqa: E731

calibration = wii.get_balance_cal()

def get_mass(data):
		return {
			'top_right':    calc_mass(data["right_top"], TOP_RIGHT),
			'bottom_right': calc_mass(data["right_bottom"], BOTTOM_RIGHT),
			'top_left':     calc_mass(data["left_top"], TOP_LEFT),
			'bottom_left':  calc_mass(data["left_bottom"], BOTTOM_LEFT),
		}

def calc_mass(raw, pos):
	# Calculates the Kilogram weight reading from raw data at position pos
	# calibration[0] is calibration values for 0kg
	# calibration[1] is calibration values for 17kg
	# calibration[2] is calibration values for 34kg
	if raw < calibration[pos][0]:
		return 0.0
	elif raw < calibration[pos][1]:
		return 17 * ((raw - calibration[pos][0]) /
						float((calibration[pos][1] -
							calibration[pos][0])))
	else: # if raw >= calibration[pos][1]:
		return 17 + 17 * ((raw - calibration[pos][1]) /
							float((calibration[pos][2] -
									calibration[pos][1])))

def animate(i):
	mass = get_mass(wii.state["balance"])
	comx = 1.0
	comy = 1.0
	try:
		total_right  = mass['top_right']   + mass['bottom_right']
		total_left   = mass['top_left']    + mass['bottom_left']
		comx = total_right / total_left
		if comx > 10:
			comx = 10 - total_right / total_left
		else:
			comx -= 10
		total_bottom = mass['bottom_left'] + mass['bottom_right']
		total_top    = mass['top_left']    + mass['top_right']
		comy = total_bottom / total_top
		if comy > 10:
			comy = 10 - total_top / total_bottom
		else:
			comy -= 10
	except BaseException:
		pass
	comx = round(comx, 2)
	comy = round(comy, 2)
	print("Center of mass: %s"%str({'x': comx, 'y': comy}))
	# plot(x,y) using pygame or any other GUI
	#ax1.clear()
	ax1.plot(comx, comy, "bo")
"""

balance_calibration = wii.get_balance_cal()
named_calibration = { 
	'right_top': balance_calibration[0],
	'right_bottom': balance_calibration[1],
	'left_top': balance_calibration[2],
	'left_bottom': balance_calibration[3],
}


def get_vals():
	weights = []
	readings = wii.state["balance"]
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

def calcweight( readings, calibrations ): 
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

def convert_relative_positions_to_coordinates(relative_positions, scaling_factor):
	# Convert relative positions to coordinates
	coordinates = relative_positions * scaling_factor

	if round(((calcweight(wii.state['balance'], named_calibration) / 100.0)*2.205)-add, 1) > 35.0:
		return coordinates
	else:
		ax1.clear()
		return [0,0]

# Example usage
sensor_positions = np.array([[68, 68], [68, -68], [-68, 68], [-68, -68]])
scaling_factor = 1

time.sleep(3)
print("Type anything to balance weight")
c = input()
add = (calcweight(wii.state['balance'], named_calibration) / 100.0)*2.205
wii.request_status()
print("Step On!")
time.sleep(3)

def animate(i) -> None:
	centroid = calculate_centroid(get_vals(), sensor_positions)
	coordinates = convert_relative_positions_to_coordinates(centroid, scaling_factor)

	ax1.plot(coordinates[0], coordinates[1], "go")

ani = animation.FuncAnimation(fig, animate, interval=10)
plt.show()