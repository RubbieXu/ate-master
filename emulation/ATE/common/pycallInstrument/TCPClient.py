import socket
from enum import Enum


class TCPClient:

    def __init__(self, instrumentName):
        if not isinstance(instrumentName, str):
            raise ValueError("Invalid instrument name")
        print(instrumentName)
        self.instrumentType = self.Instr[instrumentName[:-1]]
        self.instrumentIndex = int(instrumentName[-1])
        port = self.get_tcp_port()
        self.server_ip = "127.0.0.1"
        self.server_port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_ip, self.server_port))

    def send_message(self, message):
        print(">>" + message)
        self.client_socket.sendall(message.encode())

    def receive_message(self):

        self.client_socket.settimeout(1)
        try:
            data = self.client_socket.recv(1024).decode()
            print("<<"+data)
            return data
        except socket.timeout:
            raise TimeoutError("接收消息超时")
    def close_connection(self):
        self.client_socket.close()
    def get_tcp_port(self):
        if not isinstance(self.instrumentType, self.Instr):
            raise ValueError("无效仪器类型")

        if (self.instrumentType.value==4):
            port=23367
        elif(self.instrumentType.value==5):
            port = 23360
        else:
            port = self.instrumentType.value * 10 + self.instrumentIndex - 1+5000

        return port


    class Instr(Enum):

        Osc = 0     #示波器
        AFG = 1     #任意函数发生器
        DMM = 2     #数字万用表
        DCPwr=3     #直流电源
        LA_KingstVis=4 #金沙滩的逻辑分析仪
        SEGGERJLink=5


