import cwiid, time

button_delay = 0.5

print('Please press buttons 1 + 2 on your Wiimote now ...')
time.sleep(1)

# This code attempts to connect to your Wiimote and if it fails the program quits
try:
  Wii=cwiid.Wiimote()
except RuntimeError:
  print("Cannot connect to your Wiimote. Run again and make sure you are holding buttons 1 + 2!")
  quit()

print('Wiimote connection established!\n')
print('Go ahead and press some buttons\n')
print('Press PLUS and MINUS together to disconnect and quit.\n')

time.sleep(3)
Wii.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC | cwiid.RPT_EXT
Wii.led = 5
 #Here we handle the nunchuk, along with the joystick and the buttons
while(1):
    time.sleep(0.2)
    if Wii.state.get('nunchuk'):
        try:    
                #Here is the data for the nunchuk stick:
                #X axis:LeftMax = 25, Middle = 125, RightMax = 225
                NunchukStickX = (Wii.state['nunchuk']['stick'][cwiid.X])
                #Y axis:DownMax = 30, Middle = 125, UpMax = 225
                NunchukStickY = (Wii.state['nunchuk']['stick'][cwiid.Y])
                #The 'NunchukStickX' and the 'NunchukStickY' variables now store the stick values

                #Make it so that we can control the arm with the joystick
                if (NunchukStickX < 60):
                    print("left")
                if (NunchukStickX > 190):
                    print("right")
                if (NunchukStickY < 60):
                    print("down")
                if (NunchukStickY > 190):
                    print("up")

                #Here we create a variable to store the nunchuck button data
                #0 = no buttons pressed
                #1 = Z is pressed
                #2 = C is pressed
                #3 = Both C and Z are pressed
                ChukBtn = Wii.state['nunchuk']['buttons']
                if (ChukBtn == 1):
                    print("Z btn")
                if (ChukBtn == 2):
                    print("C btn")
                #If both are pressed the led blinks
                if (ChukBtn == 3):
                    print("both btn")


        except:
            pass
    else:
        print(Wii.state)
        time.sleep(1)