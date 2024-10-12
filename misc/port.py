from pyfirmata import Arduino, util
import time
import serial.tools.list_ports

def get_arduino_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if 'Arduino' in p.description:
            return p.device
    return None