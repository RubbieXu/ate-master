from common.pycallInstrument.TCPClient import TCPClient
import time
import os
import xml.etree.ElementTree as ET
import getpass
import subprocess
from typing import List
import psutil




class CallLA_KingstVis:
    def __init__(self, LANO:int):
        """
        - 初始化 CallLA_KingstVis 类
        - 参数:
        - LANO: 逻辑分析仪编号
        - 目前是通过与软件Kingst Vis进行通讯来控制的，多个设备端口可能会出错，无法对应识别设备和LANO的关系
        """

        self.KingstVisconfig()
        instrumentName = "LA_KingstVis"+str(LANO)
        try:
            self.client = TCPClient(instrumentName)
            self.is_initialized = True
            print("connection is success!")
        except Exception as e:
            self.is_initialized = False
            print("connection is fail!")

    def KingstVisconfig(self):
        LAexe = 0
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == "KingstVIS.exe":
                LAexe+=1
        if  LAexe==0:
            your_username = getpass.getuser()
            file_path = rf"C:\Users\{your_username}\AppData\Local\kingst\vis.config"
            # 打开XML文件
            tree = ET.parse(file_path)
            root = tree.getroot()
            ena_socket = root.find('./global/enaSocket')
            ena_socket.text = '1'
            listen_port = root.find('./global/listenPort')
            listen_port.text = '23367'
            # 保存修改后的XML文件
            tree.write(file_path, encoding='UTF-8')
            time.sleep(0.5)
            cmd_command = r'"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Kingst Vis.lnk"'
            subprocess.Popen(cmd_command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(5)

    def closeTCP(self):
        """
        - 关闭仪器连接
        """

        self.client.close_connection()

    def sendMessage(self, message):
        """
        - 发送消息到服务器
        - 参数：
        - message: 要发送的消息
        - 返回值:
        - 若消息发送成功返回 True，否则返回 False
        """
        if not self.is_initialized:
            return False
        self.client.send_message(message)

        time.sleep(0.01)
        response = self.client.receive_message()

        if response is None:
            return False
        return True


    def Configure(self, thresholdVoltage:float,sampleRate:int,sampleDepth:int,sampleTime:float):

        """
        - 使用 Configure 方法与服务器进行通信
        - 返回值:
        - 若通信成功返回 True，否则返回 False
                - thresholdVoltage                    阈值电压范围±4V，默认1.65V
                - sampleRate                          采样率，默认100M
                - sampleDepth                         采样深度，默认100M
                - sampleTime                          采样时间,默认1s

        """

        if not self.is_initialized:
            return False
        SendData = [None]*4

        SendData[0]="set-threshold-voltage "+str(thresholdVoltage)
        self.client.send_message("get-supported-sample-rate")
        time.sleep(0.1)
        response = self.client.receive_message()
        listRate = response.split()[1:]
        listRate = [int(item) for item in listRate]
        if sampleRate in listRate:
            SendData[1] = "set-sample-rate " + str(sampleRate)
        else:
            print("Error:sampleRate not in this Device("+' '.join(str(item) for item in listRate)+")")
            return  False
        SendData[2] = "set-sample-depth " + str(sampleDepth)
        SendData[3] = "set-sample-time " + str(sampleTime)

        for message in SendData:
            self.client.send_message(message)
            time.sleep(0.1)
            response = self.client.receive_message()
            if response.find('NAK') == 0:
                print(message + "设置失败")
                return False
        return True


    def Start(self,sampleTime:int):
        """
        - 使用 Start 方法与服务器进行通信
        - 返回值:

        """
        if not self.is_initialized:
            return False
        message = "start"
        self.client.send_message(message)
        # time.sleep(sampleTime)
        # response = self.client.receive_message()
        # if response.find('NAK') == 0:
        #     print(message+"设置失败")
        #     return False
        # return True

    def RecvStartACK(self):
        """
        - 接受只有采样完成后才返回的ACK信号，1s超时
        - 返回值:

        """
        if not self.is_initialized:
            return False
        response = self.client.receive_message()
        if response.find('NAK') == 0:
            print('Start'+"设置失败")
            return False
        return True

    def SaveData(self,filePath:str,selectChannel: List[int]):
        """
        - 使用 SaveData 方法与服务器进行通信
        - 返回值:

        """
        if not self.is_initialized:
            return False

        dirPath = os.path.dirname(filePath)
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)

        if len(selectChannel)==0:
            messageSelectChannel = ""
        else:
            messageSelectChannel=" --chn-select "+' '.join(str(item) for item in selectChannel)
        message = "export-data \""+ filePath+"\""+messageSelectChannel
        self.client.send_message(message)
        time.sleep(0.1)
        response = self.client.receive_message()
        if response.find('NAK') == 0:
            print(message+"设置失败")
            return False
        return True


    def SetTrigger(self,ResetAll: int, TriggerType: int, selectChannel: List[int]):
        """
        - 使用 SetTrigger 方法与服务器进行通信
        - 返回值:
            -ResetAll       TRUE时复位所有通道触发设置
            -TriggerType    要设置的触发模式，见mapping
            -selectChannel  要设置的触发通道

        """
        mapping = {
            0: "low-level",
            1: "high-level",
            2: "pos-edge",
            3: "neg-edge"
        }
        if not self.is_initialized:
            return False
        if ResetAll:
            self.client.send_message("set-trigger --reset")
            time.sleep(0.1)
            response = self.client.receive_message()
            if response.find('NAK') == 0:
                print("set-trigger --reset设置失败")
                return False
        messageSelectChannel = " " + ' '.join(str(item) for item in selectChannel)
        message = "set-trigger --" + mapping.get(TriggerType)+ messageSelectChannel
        self.client.send_message(message)
        time.sleep(0.1)
        response = self.client.receive_message()
        if response.find('NAK') == 0:
            print(message + "设置失败")
            return False
        return True



