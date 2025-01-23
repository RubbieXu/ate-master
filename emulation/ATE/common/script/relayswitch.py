import threading
import os
import time
import serial
import logging
from common.script.file_control import *
from datetime import datetime
from serial import Serial
from common.script import Serial_Port

serial_control = Serial_Port
relayswitch_data = read_yaml('./config/serial_config.yaml')
relayswitch = relayswitch_data[0].get('relay_switch')


class SwitchInit:

    def __init__(self, serial_port, baud_rate, timeout=5):
        self.serial_port = Serial(port=serial_port, baudrate=baud_rate, timeout=timeout)

    def on(self):
        on = bytes.fromhex('A0 01 01 A2')
        self.serial_port.write(on)
        # time.sleep(3)  # 从6改为3

    def off(self):
        off = bytes.fromhex('A0 01 00 A1')
        self.serial_port.write(off)
        # time.sleep(3)  # 从6改为3

    def switching(self):
        on = bytes.fromhex('A0 01 01 A2')
        off = bytes.fromhex('A0 01 00 A1')
        self.serial_port.write(off)
        time.sleep(0.1)
        self.serial_port.write(on)
        time.sleep(0.1)
        self.serial_port.readline(100000).decode('latin-1')
        # self._start_logcat_power_up_down(8)
        # content = open_core1_log()
        # self.serial_port.readline(10000).decode('utf-8')
        # time.sleep(8)# 12改成8

    def close(self):
        self.serial_port.close()
switch = SwitchInit(relayswitch['port'], baud_rate=relayswitch['baud'], timeout=relayswitch['timeout'])