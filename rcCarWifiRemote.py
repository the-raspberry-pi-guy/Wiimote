from imu import MPU6050
import time
import network
import socket
from machine import Pin, I2C

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
imu = MPU6050(i2c)
btn_a = Pin(8, Pin.IN, Pin.PULL_UP)
btn_b = Pin(26, Pin.IN, Pin.PULL_UP)
btn_left = Pin(21, Pin.IN, Pin.PULL_UP)
btn_right = Pin(20, Pin.IN, Pin.PULL_UP)
btn_up = Pin(22, Pin.IN, Pin.PULL_UP)
btn_down = Pin(7, Pin.IN, Pin.PULL_UP)
red = Pin(15, Pin.OUT)
green = Pin(12, Pin.OUT)
blue = Pin(11, Pin.OUT)

red.value(1)
green.value(0)
blue.value(1)

ssid = 'Stoltzfus-2G' #Stoltzfus-2G
password = 'Farhills' #Farhills

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() is False:
        print('Waiting for connection...')
        time.sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def connect_socket():
    connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    connection.settimeout(0.4)
    return connection

try:
    ip = connect()
    connection = connect_socket()
except KeyboardInterrupt:
    machine.reset()

moving = 0
a_held = False
b_held = False
while True:
    if not btn_b.value():
        if not b_held:
            print("stop")
            connection.sendto(b"CMD_MOTOR#0#0#0#0", ("192.168.1.140", 4000))
            moving = 0
            a_held = True
            b_held = True
    elif not btn_a.value():
        if not a_held:
            connection.sendto(b"CMD_USONIC", ("192.168.1.140", 4000))
            try:
                value = connection.recvfrom(1024)[0].decode()
                print(value)
                if value == 'e':
                    red.value(1)
                    green.value(0)
                    blue.value(1)
                elif value == 'd':
                    red.value(0)
                    green.value(1)
                    blue.value(1)
            except:
                red.value(1)
                green.value(1)
                blue.value(0)
            a_held = True
            time.sleep(0.2)
    elif b_held:
        b_held = False
    elif a_held:
        a_held = False
    if 1 != moving and not btn_up.value() :
        print("start")
        connection.sendto(b"CMD_MOTOR#2000#2000#2000#2000", ("192.168.1.140", 4000))
        moving = 1
    elif 2 != moving and not btn_down.value():
        print("rev")
        connection.sendto(b"CMD_MOTOR#-1500#-1500#-1500#-1500", ("192.168.1.140", 4000))
        moving = 2
    elif 3 != moving and not btn_right.value():
        print("right")
        connection.sendto(b"CMD_MOTOR#1000#1000#-1000#-1000", ("192.168.1.140", 4000))
        moving = 3
    elif 4 != moving and not btn_left.value():
        print("left")
        connection.sendto(b"CMD_MOTOR#-1000#-1000#1000#1000", ("192.168.1.140", 4000))
        moving = 4
    elif not btn_up.value():
        pass
    elif not btn_down.value():
        pass
    elif not btn_right.value():
        pass
    elif not btn_left.value():
        pass
    elif moving > 0:
        print("stop")
        connection.sendto(b"CMD_MOTOR#0#0#0#0", ("192.168.1.140", 4000))
        moving = 0