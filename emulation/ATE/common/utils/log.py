# coding=utf-8
import os
import time
import logging
import sys
import logging.config


class Log(object):
    def __init__(self, name: str or None = None):
        self.logger = logging.getLogger(name=name)
        self.logger.setLevel(level=logging.INFO)
        self.log_time = name + "_" + time.strftime("%Y_%m_%d_%H_%M_%S")
        decode_dir = "logs"
        if not os.path.exists(decode_dir):
            os.mkdir(decode_dir)
        self.log_path = "./logs/"
        self.log_name = self.log_path + self.log_time + '.log'
        if not self.logger.handlers:
            self._create_log_file()
            self._create_terminal_log_file()  # 添加创建终端日志文件的调用

    def _create_log_file(self):
        log_folder = os.path.join(self.log_path, self.log_time)
        if not os.path.exists(log_folder):
            os.mkdir(log_folder)
        file_path = os.path.join(log_folder, self.log_time + ".log")
        fh = logging.FileHandler(file_path, 'a', encoding='utf-8')
        fh.setLevel(level=logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(level=logging.DEBUG)
        formatter = logging.Formatter('[%(process)d][%(asctime)s %(filename)s-%(lineno)s %(levelname)s]:%(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def _create_terminal_log_file(self):
        terminal_log_path = os.path.join(self.log_path, self.log_time, "terminal.log")
        terminal_fh = logging.FileHandler(terminal_log_path, 'a', encoding='utf-8')
        terminal_fh.setLevel(level=logging.DEBUG)
        formatter = logging.Formatter('[%(process)d][%(asctime)s]:%(message)s')
        terminal_fh.setFormatter(formatter)

        # 获取默认的StreamHandler（sys.stdout）并设置其格式
        logger = logging.getLogger('terminal_logger')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(terminal_fh)

        # 缓存原始的sys.stdout，并将其重定向到logger中
        original_stdout = sys.stdout
        sys.stdout = StreamToLogger(logger, logging.INFO, original_stdout)

        # 将logger对象返回，以便在其他地方使用
        return logger

    def get_log(self):
        self.logger.propagate = False
        return self.logger


class StreamToLogger():
    def __init__(self, logger, log_level=logging.INFO, original_stdout=None):
        self.logger = logger
        self.log_level = log_level
        self.original_stdout = original_stdout

    def write(self, message):
        message = message.replace('\033', '').replace('[32;22m', '').replace('[0m', '').replace('[32;22m', '') \
            .replace('[31;1mE', '').replace('?[32;22m', '').replace('?[0m', '').replace('?[31;1m', '') \
            .replace("[32;22mI", '').replace('[36;1mA', '').replace('[31;1mE', '') \
            .replace('[36;1mA', '').replace('[33;1mW', '').replace('[35;22mD', '').replace('[34;22mV', '')
        self.logger.log(self.log_level, message.strip())
        if self.original_stdout:
            self.original_stdout.write(message)

    def flush(self):
        pass

    def isatty(self):
        return False


log = Log('autotest').get_log()
