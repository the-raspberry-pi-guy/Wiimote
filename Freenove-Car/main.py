import numpy as np
import cwiid, time  # noqa: E401

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

