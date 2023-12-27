import time
import cwiid
wii=cwiid.Wiimote()

start = time.time()
while True:
    val = wii.state
    if val["ext_type"] == 3:
        break
end_time = time.time()

print("total time taken:", end_time - start)