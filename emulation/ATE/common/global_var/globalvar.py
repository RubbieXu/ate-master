import os
import sys

file_dir = os.path.dirname(__file__)
print(file_dir)
spi_dir = file_dir + '\\..\\..\\..' + '\\usr'
print(spi_dir)
sys.path.append(spi_dir)
import test_shell


ateif = test_shell.ateinterface()


