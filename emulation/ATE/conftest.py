import pytest
# import serial
import os
import threading
import time
import json
import sys
from common.script.file_control import *
from common.global_var.globalvar import *


project_name = 'DDIC'

if project_name == 'IPC':
    @pytest.fixture(scope="session", autouse=True)
    def setup_interface_A(request):
        pass


    @pytest.fixture(scope="session", autouse=True)
    def setup_interface_B(request):
        pass
 
else:
    @pytest.fixture(scope="session", autouse=True)
    def setup_interface(request):
        pass
