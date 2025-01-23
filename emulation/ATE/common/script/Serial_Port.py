import time
# import serial
import logging
import threading
import os

from datetime import datetime
from common.utils.log import log
import binascii

core1_temp_log_path = './logs/core1_log'
core2_temp_log_path = './logs/core2_log'
core1_logcat_path = './logs/core1_logcat.txt'
core2_logcat_path = './logs/core2_logcat.txt'

class SerialPort:
    def __init__(self, serial_port):
        self.serial_port = serial_port

    def send_data(self, size):

        rsp = self.serial_port.readline(size)
        return rsp

    def write_data(self, data):
        if self.serial_port:
            self.serial_port.write(data)

    def logcat_save_system_core1(self, play_time):
        start_time = time.time()
        while time.time() - start_time < float(play_time):
            line = self.send_data(100000).decode('latin-1')  # 可以解码乱码符号等
            # time.sleep(30)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(line.replace('\n', ''))
            data = line.replace('\033', '').replace('[32;22m', '').replace('[0m', '').replace('\n', '')
            log_message = f'[{timestamp}]:{data}'
            with open(core1_temp_log_path, 'a', encoding='utf-8') as f:
                f.writelines(log_message + '\n')
                f.flush()

    def _start_system_core1_loop(self, play_time):
        logging.getLogger().setLevel(logging.INFO)
        if os.path.exists(core1_temp_log_path):
            os.remove(core1_temp_log_path)
        self._read_thread = threading.Thread(target=self.logcat_save_system_core1(play_time), name='read_loop',
                                             daemon=True)
        self._read_thread.start()

    def logcat_save_system_core2(self, play_time):
        start_time = time.time()
        while time.time() - start_time < float(play_time):
            line = self.send_data(100000).decode('latin-1')
            # time.sleep(30)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(line.replace('\n', ''))
            data = line.replace('\033', '').replace('[32;22m', '').replace('[0m', '').replace('\n', '')
            log_message = f'[{timestamp}]:{data}'
            with open(core2_temp_log_path, 'a', encoding='utf-8') as f:
                f.writelines(log_message + '\n')
                f.flush()

    def _start_system_core2_loop(self, play_time):
        logging.getLogger().setLevel(logging.INFO)
        if os.path.exists(core2_temp_log_path):
            os.remove(core2_temp_log_path)
        self._read_thread = threading.Thread(target=self.logcat_save_system_core2(play_time), name='read_loop',
                                             daemon=True)
        self._read_thread.start()

    def log_check_timeout(self, check_str_list=None, timeout=None):
        start_time = time.time()
        check_passed = False
        while True:
            # 读取串口数据
            response = self.serial_port.readline(100000).decode('latin-1')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_message = f'[{timestamp}]:{response}'
            with open(core1_logcat_path, 'a', encoding='utf-8') as f:
                f.writelines(log_message + '\n')
                f.flush()
            # 检查返回的数据是否包含"pass"
            if all(item in response for item in check_str_list):
                check_passed = True
                return response

            # 如果超过timeout没，判断为失败
            if time.time() - start_time > timeout:
                break
        # 关闭串口
        # self.serial_port.close()
        return check_passed
    def log_check_timeout_ram(self, check_str_list=None, timeout=None):
        start_time = time.time()
        # check_passed = False
        while True:
            # 读取串口数据
            response = self.serial_port.readline(1000000).decode('latin-1')
            if all(item in response for item in check_str_list):
                return response
            # 如果超过timeout没有返回，判断为失败
            if time.time() - start_time > timeout:
                log.info("log_check_timeout_ram  overtime")
                break
        return False