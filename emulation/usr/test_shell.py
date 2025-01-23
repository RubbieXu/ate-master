import os
import sys
file_dir = os.path.dirname(__file__)
spi_dir = file_dir + '\\..' + '\\drivers'
sys.path.append(spi_dir)
from spi import spi
from test_itf import test_itf

class ateinterface:
    def __init__(self):
        self.dev_spi = spi()
        self.test_case_itf = test_itf(self.dev_spi)
        self.test_case_table = {
            'if' : self.test_case_itf.test_command_table,
        }

    def execcmd(self, para_list = []):
        # print(para_list)
        module_str = para_list[0]
        module_cmd_table = self.test_case_table[module_str]
        
        cmd_str = para_list[1]
        if cmd_str not in module_cmd_table:
            print(f'error: command "{module_str} {cmd_str}" is not exist')
            return
        # get function for test command
        test_cmd_func = module_cmd_table[cmd_str]
        retval =  test_cmd_func(para_list[2:])
        return retval


if __name__ == '__main__':
    dev_spi = spi()
    test_case_itf = test_itf(dev_spi)
    # test module table
    test_case_table = {
        'if' : test_case_itf.test_command_table,
    }
    print('start to test, commdn "exit" to exit test')
    while True:
        test_cmd_str = input('>')
        # remove space from header and tail
        test_cmd_str = test_cmd_str.removeprefix(' ')
        test_cmd_str = test_cmd_str.removesuffix(' ')
        test_cmd_args = test_cmd_str.split()
        args_len = len(test_cmd_args)
        # print test modules.
        if args_len == 0:
            print("Test modules:")
            modules = list(test_case_table.keys())
            for module_name in modules:
                print(f'\t{module_name}')
            continue
        # get test module.
        module_str = test_cmd_args[0]
        if module_str == 'exit':
            exit()
        if module_str not in test_case_table:
            print(f'error: no test module "{module_str}"')
            continue
        # get test command.
        module_cmd_table = test_case_table[module_str]
        if args_len == 1:
            print(f'commands for test module "{module_str}"')
            cmds = list(module_cmd_table.keys())
            for cmd in cmds:
                print(f'\t{cmd}')
            continue
        cmd_str = test_cmd_args[1]
        if cmd_str not in module_cmd_table:
            print(f'error: command "{module_str} {cmd_str}" is not exist')
            continue
        # get function for test command
        test_cmd_func = module_cmd_table[cmd_str]
        para_list = []
        para_ok = True
        if args_len > 2:
            for cmd_arg in test_cmd_args[2:]:
                # try:
                #     if '0x' == cmd_arg[0:2] or '0X' == cmd_arg[0:2]:
                #         cmd_number = int(cmd_arg, 16)
                #     else:
                #         cmd_number = int(cmd_arg, 10)
                # except:
                #     print(f'error: parameter {cmd_arg} is not number')
                #     para_ok = False
                #     break
                para_list.append(cmd_arg)
        if not para_ok:
            continue
        test_cmd_func(para_list)

