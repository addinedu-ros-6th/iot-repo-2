import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import serial
import struct
import time

def connect():
    conn = serial.Serial(port='/dev/ttyACM1', baudrate= 9600, timeout= 1)
    return conn

def send(conn):
    while True:
        data = input("input : ")
        if (data == 'q'):
            break
        if (data == 'w'):
            sendw(b'SLC',0)
        elif (data == 'e'):
            sendw(b'SHT',1)
        elif (data == 'r'):
            sendw(b'SLC',2)
        elif (data == 't'):
            sendw(b'SLC',3)
        time.sleep(0.1)
        if (conn.readable()):
            recv = conn.readline().decode().strip('\r\n')
            if (len(recv) > 0):
                print("recv : "+ str(recv))
    return

def sendw(command, data):
    print("send")
    req_data = struct.pack('<3sBc', command, data, b'\n')
    conn.write(req_data)
    print(req_data)
    return

if __name__ == "__main__":
    conn = connect()
    send(conn)
    conn.close()