from common.pycallInstrument.TCPClient import TCPClient
import time
class CallDCPwr:
    def __init__(self, DCPwrNO:int):
        """
        - 初始化 CallDCPwr 类
        - 参数:
        - DCPwrNO: 示波器编号
        """
        instrumentName = "DCPwr"+str(DCPwrNO)
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



    def openInstr(self,reset:int):
        """
        - 使用 openInstr 方法与服务器进行通信
        - 返回值:
        - 若通信成功返回 True，否则返回 False

        - 输入参数reset为bool，用来表示示波器是否需要reset
        """
        command = "openInstr"
        if not self.is_initialized:

            return False
        message= command+" "+str(reset)
        self.client.send_message(message)
        if reset ==1:
            time.sleep(5)   #示波器在进行Reset
        time.sleep(2)       #示波器在进行Default Instrument Setup
        # 上述延时是安照示波器Demo程序设置，延时较长，可按实际使用来修改

        response = self.client.receive_message()
        response_mapping = {
            command+" Success": True,
            command+" Fail": False,
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
        message= command
        self.client.send_message(message)
        response = self.client.receive_message()
        response_mapping = {
            command+" Success": True,
            command+" Fail": False,
        }
        if response in response_mapping:
            return response_mapping[response]
        else:
            print("非正常通讯返回")
        return False


    def Configure(self, channel:int,OutputType:int,OutputLevel:float):

        """
        - 使用 Configure 方法与服务器进行通信
        - 返回值:
        - 若通信成功返回 True，否则返回 False

                - OutputType              0:Voltage；1:Current
                - OutputLevel

            - Configure_Channel(0,1)
            - 通道1,电压输出,1V

        """
        command = "Configure"
        if not self.is_initialized:
            return False
        message = command+" "+str(OutputType)+" "+str(OutputLevel)
        self.client.send_message(message)
        time.sleep(0.8)
        response = self.client.receive_message()
        response_mapping = {
            command+" Success": True,
            command+" Fail": False,
        }
        if response in response_mapping:
            return response_mapping[response]
        else:
            print("非正常通讯返回")
        return False


    def Enable_Output(self,  Enable_Output: int):

        """
        - 使用 Enable_Output 方法与服务器进行通信
        - 返回值:
        - 若通信成功返回 True，否则返回 False

                - Enable_Output

            - Enable_Output(1)
            - 输出on

        """
        command = "Enable_Output"
        if not self.is_initialized:
            return False
        message = command+" " + str(Enable_Output)

        self.client.send_message(message)

        time.sleep(0)

        response = self.client.receive_message()
        response_mapping = {
            command+" Success": True,
            command+" Fail": False,
        }
        if response in response_mapping:
            return response_mapping[response]
        else:
            print("非正常通讯返回")
        return False

    def ReadData(self):
        """
        使用 ReadData 方法与服务器进行通信
        返回值:
        若通信成功返回 实际数据，否则返回 null
        串口未初始化则，返回null


        """
        MesData: list = []
        command = "ReadData"
        if not self.is_initialized:
            return MesData
        message = command
        self.client.send_message(message)
        time.sleep(0.2)
        response = self.client.receive_message()
        if response.startswith(command + " Success"):
            data_str = response.split(" ")[-2:]  # 获取数据部分
            MesData = [float(d) for d in data_str]  # 将数据转换为浮点数
        return MesData



