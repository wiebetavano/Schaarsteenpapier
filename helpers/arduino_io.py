import time

import serial.tools.list_ports
from serial import Serial

from helpers.gui_helper import putCountDown


class ArduinoLink(object):
    def __init__(self, baudrate=9600, port=None, timeout=1):
        self.baudrate = baudrate
        self.port = port
        self.timeout = timeout
        self.link = Serial()

    def handshake(self, ser_conn):
        print('Trying Handshake')
        # We try 3 times, the first byte might restart the aruduino
        for _ in range(3):
            ser_conn.write(b'Q')
            time.sleep(.5)
            response = ser_conn.readline()
            if response == b'R':
                print(f'Handshake succesfull on {ser_conn.port}')
                return True
        else:
            return False

    def test_ports_depr(self):
        # go over available ports and try a handshake on them,
        # if succesfull we open the connection
        ports = self.list_ports()
        for port in ports:
            try:
                print(port)
                ard = Serial(port, self.baudrate, timeout=self.timeout)
                if self.handshake(ard):
                    self.link.port = port
                    self.link.baudrate = self.baudrate
                    self.link.timeout = self.timeout
                    self.open()
                    print(f'Open connection on {port}')
            except Exception as e:
                print(e)
    
    def test_ports(self, port= '/dev/ttyUSB0'):
        try:
            self.link.port = port
            self.link.baudrate = self.baudrate
            self.link.timeout = self.timeout
            self.open()
        except Exception as e:
            if port == '/dev/ttyUSB0':
                self.test_ports(port='/dev/ttyUSB1')
            else:
                print(e)


    def open(self):
        if not self.link.is_open:
            self.link.open()

    def write(self, message, verbose=False):
        self.open()
        if isinstance(message, bytes):
            pass
        else:
            message = chr(message).encode()
        for idx in range(20):
            try:
                self.link.write(message)
                break
            except:
                time.sleep(0.1)
                if idx == 19:
                    self.test_ports()
                    self.write(message)

        if verbose:
            print(f'wrote {message} to {self.link.port}')

    def readline(self):
        # Read bytes from the connection untill a \n is reached
        self.open()
        return self.link.readline()

    def read(self):
        # Read the first available byte from the connection
        self.open()
        return self.link.read()

    def list_ports(self):
        # we build a list of all available ports on this machine
        comports = serial.tools.list_ports.comports()
        ports = [port.device for port in comports if port.device]
        return ports
