import sys
from time import sleep
import cwiid

def main():
	#Connect to address given on command-line, if present
	print('Put Wiimote in discoverable mode now (press 1+2)...')
	global wiimote
	if len(sys.argv) > 1:
		wiimote = cwiid.Wiimote(sys.argv[1])
	else:
		wiimote = cwiid.Wiimote()

	wiimote.rpt_mode = cwiid.RPT_BALANCE
	wiimote.request_status()
	balance_calibration = wiimote.get_balance_cal()
	named_calibration = { 'right_top': balance_calibration[0],
						  'right_bottom': balance_calibration[1],
						  'left_top': balance_calibration[2],
						  'left_bottom': balance_calibration[3],
						}

	sleep(3)
	print("Type anything to balance weight")
	c = sys.stdin.read(1)
	add = (calcweight(wiimote.state['balance'], named_calibration) / 100.0)*2.205
	wiimote.request_status()
	print("Step On!")
	sleep(3)

	while True:
		print("Type q to quit, or anything else to report your weight")
		c = input()
		if c == 'q':
			break
		wiimote.request_status()
		print(round(((calcweight(wiimote.state['balance'], named_calibration) / 100.0)*2.205)-add, 1), "Lbs")

	return 0

def calcweight( readings, calibrations ): 
	"""
	Determine the weight of the user on the board in hundredths of a kilogram
	"""
	weight = 0
	for sensor in ('right_top', 'right_bottom', 'left_top', 'left_bottom'):
		reading = readings[sensor]
		calibration = calibrations[sensor]
	
		if reading > calibration[2]:
			print("Warning", sensor, "reading above upper calibration value")
		# 1700 appears to be the step the calibrations are against.
		# 17kg per sensor is 68kg, 1/2 of the advertised Japanese weight limit.
		if reading < calibration[1]:
			weight += 1700 * (reading - calibration[0]) / (calibration[1] - calibration[0])
		else:
			weight += 1700 * (reading - calibration[1]) / (calibration[2] - calibration[1]) + 1700

	return weight

if __name__ == "__main__":
	sys.exit(main())