import cwiid
from time import time, asctime, sleep, perf_counter
from numpy import *
from pylab import *
import math
import numpy as np
from operator import add
HPF = 0.98
LPF = 0.02

def calibrate(wiimote):
    print("Keep the remote still")
    sleep(3)
    print("Calibrating")
    
    messages = wiimote.get_mesg()
    i=0
    accel_init = []
    angle_init = []
    while (i<1000):
        sleep(0.01)
        messages = wiimote.get_mesg()
        for mesg in messages:
            # Motion plus:
            if mesg[0] == cwiid.MESG_MOTIONPLUS:
                if record:
                    angle_init.append(mesg[1]['angle_rate'])
            # Accelerometer:
            elif mesg[0] == cwiid.MESG_ACC:
                if record:
                    accel_init.append(list(mesg[1]))
        i+=1

    accel_init_avg = list(np.mean(np.array(accel_init), axis=0))
    print(accel_init_avg)
    angle_init_avg = sum(angle_init)/len(angle_init)
    print("Finished Calibrating")
    return (accel_init_avg, angle_init_avg)
    
def plotter(plot_title, timevector, data, position, n_graphs):
   subplot(n_graphs, 1, position)
   plot(timevector, data[0], "r",
        timevector, data[1], "g",
        timevector, data[2], "b")
   xlabel("time (s)")
   ylabel(plot_title)

print("Press 1+2 on the Wiimote now")
wiimote = cwiid.Wiimote()

# Rumble to indicate a connection
wiimote.rumble = 1
print("Connection established - release buttons")
sleep(0.2)
wiimote.rumble = 0
sleep(1.0)

wiimote.enable(cwiid.FLAG_MESG_IFC | cwiid.FLAG_MOTIONPLUS)
wiimote.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC | cwiid.RPT_MOTIONPLUS

accel_init, angle_init = calibrate(wiimote)
str = ""
print("Press plus to start recording, minus to end recording")
loop = True
record = False
accel_data = []
angle_data = []
messages = wiimote.get_mesg()
while (loop):
   sleep(0.01)
   messages = wiimote.get_mesg()
   for mesg in messages:
       # Motion plus:
       if mesg[0] == cwiid.MESG_MOTIONPLUS:
           if record:
               angle_data.append({"Time" : perf_counter(), \
                   "Rate" : mesg[1]['angle_rate']})
       # Accelerometer:
       elif mesg[0] == cwiid.MESG_ACC:
           if record:               
               accel_data.append({"Time" : perf_counter(), "Acc" : [mesg[1][i] - accel_init[i] for i in range(len(accel_init))]})
       # Button:
       elif mesg[0] == cwiid.MESG_BTN:
           if mesg[1] & cwiid.BTN_PLUS and not record:
               print("Recording - press minus button to stop")
               record = True
               start_time = perf_counter()
           if mesg[1] & cwiid.BTN_MINUS and record:
               if len(accel_data) == 0:
                   print("No data recorded")
               else:
                   print("End recording")
                   print("{0} data points in {1} seconds".format(
                       len(accel_data), perf_counter() - accel_data[0]["Time"]))
               record = False
               loop = False
       else:
           pass

wiimote.disable(cwiid.FLAG_MESG_IFC | cwiid.FLAG_MOTIONPLUS)
if len(accel_data) == 0:
   sys.exit()


timevector = []
a = [[],[],[]]
v = [[],[],[]]
p = [[],[],[]]
last_time = 0
velocity = [0,0,0]
position = [0,0,0]

for n, x in enumerate(accel_data):
   if (n == 0):
       origin = x
   else:
       elapsed = x["Time"] - origin["Time"]
       delta_t = x["Time"] - last_time
       timevector.append(elapsed)
       for i in range(3):
           acceleration = x["Acc"][i] - origin["Acc"][i]
           velocity[i] = velocity[i] + delta_t * acceleration
           position[i] = position[i] + delta_t * velocity[i]
           a[i].append(acceleration)
           v[i].append(velocity[i])
           p[i].append(position[i])
   last_time = x["Time"]

n_graphs = 3
if len(angle_data) == len(accel_data):
   n_graphs = 5
   angle_accel = [(math.pi)/2 if (j**2 + k**2)==0 else math.atan(i/math.sqrt(j**2 + k**2)) for i,j,k in zip(a[0],a[1],a[2])]
   ar = [[],[],[]] # Angle rates
   aa = [[],[],[]] # Angles
   angle = [0,0,0]
   for n, x in enumerate(angle_data):
       if (n == 0):
           origin = x
       else:
           delta_t = x["Time"] - last_time
           for i in range(3):
               rate = x["Rate"][i] - origin["Rate"][i]
               angle[i] = HPF*(np.array(angle[i]) + delta_t * rate) + LPF*np.array(angle_accel)
               ar[i].append(rate)
               aa[i].append(angle[i])
       last_time = x["Time"]


plotter("Acceleration", timevector, a, 1, n_graphs)
if n_graphs == 5:
   plotter("Angle Rate", timevector, ar, 4, n_graphs)
   plotter("Angle", timevector, aa, 5, n_graphs)

show()