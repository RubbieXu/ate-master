# coding=utf-8
import logging
import pytest
import os
import yaml
import re
from datetime import datetime, timedelta
from common.utils.log import log, Log
import binascii
import time
from common.script.Serial_Port import SerialPort

core1_temp_log_path = './logs/core1_log'
core2_temp_log_path = './logs/core2_log'


def check_serial_alive(setup_serial1, setup_serial2, timeout=5):
    task_info_show = 'ps\r'
    start_time = time.time()
    serial_port_1 = SerialPort(setup_serial1)
    serial_port_1.write_data(task_info_show.encode())
    serial_port_2 = SerialPort(setup_serial2)
    serial_port_2.write_data(task_info_show.encode())
    is_alive = False
    serial_port_1._start_system_core1_loop(1)
    content1 = open_core1_log()
    serial_port_2._start_system_core2_loop(1)
    content2 = open_core2_log()
    while time.time() - start_time < timeout:
        if 'exec directly!' in content1 \
                and 'exec directly!' in content2:
            is_alive = True
        time.sleep(0.1)
    return is_alive


# log = Log('test_crc16.log').get_log()
def read_power_log(setup_serial1, setup_serial2):
    print("读取继电器上下电日志：")
    serial_port_1 = SerialPort(setup_serial1)
    serial_port_1._start_system_core1_loop(2)

    serial_port_2 = SerialPort(setup_serial2)
    serial_port_2._start_system_core2_loop(2)
    print("读取日志完毕")


def open_core1_log():
    print("Please open log ")
    with open('./logs/core1_log') as f:
        content = f.read()
        # print("core log日志：：：：：\n", content)
    with open('./logs/core1_logcat.txt', 'a') as f:
        f.write(content)
        # log.info("open log successful")
    # os.rename('./logs/core1_logcat.txt',Log.log_folder)
    return content


def open_core2_log():
    print("open log successful ")

    with open('./logs/core2_log') as f:
        content = f.read()
        log.info("open log successful ")
        # print(content)
    with open('./logs/core2_logcat.txt', 'a') as f:
        f.write(content)
    return content


def hse_open_core1_log():
    print("Please open log ")
    with open('./logs/core1_log') as f:
        content = f.read()
        # print("core log日志：：：：：\n", content)
    with open('./logs/core1_logcat.txt', 'a') as f:
        f.write(content)
        # log.info("open log successful")

    return content


def read_yaml(path):
    yaml_file = open(path, 'r', encoding='utf-8')
    with yaml_file as f:
        content = yaml.load(f, Loader=yaml.Loader)
    return content
