from common.pycallInstrument.TCPClient import TCPClient
import time
import re


class CallDMM:
    def __init__(self, DMMNO: int):
        """
        - 初始化 CallDMM 类
        - 参数:
        - DMMNO: 示波器编号
        """
        instrumentName = "DMM" + str(DMMNO)
        self.client = TCPClient(instrumentName)

        instr_info = self.client.receive_message()

        if instr_info is None:
            self.is_initialized = False
        else:
            self.is_initialized = True

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

    def openInstr(self):
        """
        - 使用 openInstr 方法与服务器进行通信
        - 返回值:
        - 若通信成功返回 True，否则返回 False

        - 输入参数reset为bool，用来表示示波器是否需要reset
        """
        command = "openInstr"
        if not self.is_initialized:
            return False
        message = command
        self.client.send_message(message)

        time.sleep(3.5)  # 示波器在进行Default Instrument Setup
        # 上述延时是安照示波器Demo程序设置，延时较长，可按实际使用来修改

        response = self.client.receive_message()
        response_mapping = {
            command + " Success": True,
            command + " Fail": False,
        }
        if response in response_mapping:
            return response_mapping[response]
        else:
            print("非正常通讯返回")
        return False

    def closeInstr(self):
        """
        - 使用 closeInstr 方法与服务器进行通信
        - 返回值:
        - 若通信成功返回 True，否则返回 False

        - 输入参数reset为bool，用来表示示波器是否需要reset
        """
        command = "closeInstr"
        if not self.is_initialized:
            return False
        message = command
        self.client.send_message(message)
        response = self.client.receive_message()
        response_mapping = {
            command + " Success": True,
            command + " Fail": False,
        }
        if response in response_mapping:
            return response_mapping[response]
        else:
            print("非正常通讯返回")
        return False

    def Configure_Channel(self, channel: int, DMM_Test_type: bytes, DMM_Range: bytes):

        """
        - 使用 Configure_Channel 方法与服务器进行通信
        - 返回值:
        - 若通信成功返回 True，否则返回 False
                - channel                    通道
                - DMM_Test_type              见下备注
                - DMM_Range          见下备注
            - Configure_Channel(1,0,0)
            - 通道1,DC模式,量程±50mV
            - 备注:
            - #define VIC8246A_DCV    0     0x30
            - #define VIC8246A_ACI    1
            - #define VIC8246A_DCI    2
            - #define VIC8246A_ACI    3
            - #define VIC8246A_OHM_2W 4
            - #define VIC8246A_OHM_4W 5
            - #define VIC8246A_CONT   6
            - #define VIC8246A_DIODE  7
            - #define VIC8246A_FREQ   8
            - #define VIC8246A_CAP    9
            - #define VIC8246A_TEMP   A
            - #define VIC8246A_RTD    B
            - #define VIC8246A_dBm    C      0x3C

            - //定义VIC8246A的范围
            - #define VIC8246A_DCV_50mV    0
            - #define VIC8246A_DCV_500mV   1
            - #define VIC8246A_DCV_5V      2
            - #define VIC8246A_ACV_50mV    0
            - #define VIC8246A_ACV_500mV   1
            - #define VIC8246A_DCI_500uA   0
            - #define VIC8246A_DCI_5000uA  1
        """
        command = "Configure_Channel"
        if not self.is_initialized:
            return False
        # DMM_Test_type = int(DMM_Test_type, 16)
        # DMM_Range = int(DMM_Range, 16)
        message = command + " " + str(channel) + " " + chr(DMM_Test_type + 0x30) + " " + chr(DMM_Range + 0x30)
        self.client.send_message(message)
        time.sleep(0.8)
        response = self.client.receive_message()
        response_mapping = {
            command + " Success": True,
            command + " Fail": False,
        }
        if response in response_mapping:
            print("!!!!!!!!!!!")
            return response_mapping[response]
        else:
            print("非正常通讯返回")
        return False

    def ReadData(self):
        """
        - 使用 ReadData 方法与服务器进行通信
        - 返回值:
        - 若通信成功返回 实际数据，否则返回 -999
        - 串口未初始化则，返回-9999
        """
        DMMData: float = -999
        command = "ReadData"
        if not self.is_initialized:
            DMMData = -9999
            return DMMData
        message = command

        self.client.send_message(message)

        time.sleep(0.1)
        response = self.client.receive_message()
        if response.startswith(command + " Success"):
            # DMMData = 1
            match = re.search(r"\+[\d.]+", response.split(" ")[-1])
            if match:
                result = match.group()
            DMMData = float(result)
        else:
            print("非正常通讯返回")
        return DMMData

        # response = self.client.receive_message()
        # if response.startswith(command + " Success"):
        #     # DMMData = 1
        #     print("2222222222222")
        #     DMMData = float(response.split(" ")[-1])
        # else:
        #     print("非正常通讯返回")
        #
        # return DMMData
