from common.pycallInstrument.TCPClient import TCPClient
import time


class CallOSC:
    def __init__(self, OscNO: int):
        """
        - 初始化 CallOsc 类
        - 参数:
        - OscNO: 示波器编号
        """
        instrumentName = "Osc" + str(OscNO)
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

    def openInstr(self, reset: int):
        """
        - 使用 openInstr 方法与服务器进行通信
        - 返回值:
        - 若通信成功返回 True，否则返回 False

        - 输入参数reset为bool，用来表示示波器是否需要reset
        """
        command = "openInstr"
        if not self.is_initialized:
            return False
        message = command + " " + str(reset)
        self.client.send_message(message)
        if reset == 1:
            time.sleep(5)  # 示波器在进行Reset
        time.sleep(2)  # 示波器在进行Default Instrument Setup
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

    def Configure_Channel(self, channel: int, Vertical_Coupling: int, probe_Attenuation: float, Vertical_Range: float,
                          Vertical_Offset: float):

        """
        - 使用 Configure_Channel 方法与服务器进行通信
        - 返回值:
        - 若通信成功返回 True，否则返回 False
                - channel                    通道
                - Vertical_Coupling          0:DC;1:AC;2:Ground
                - probe_Attenuation          探头衰减
                - Vertical_Range             垂直范围
                - Vertical_Offset            垂直偏移
            - Configure_Channel(1,0,1.0,50,0)
            - 通道1,DC模式,探头衰减系数:1.0,垂直范围5V,垂直偏移0V
        """
        command = "Configure_Channel"
        if not self.is_initialized:
            return False
        message = command + " " + str(channel) + " " + str(Vertical_Coupling) + " " + str(
            probe_Attenuation) + " " + str(Vertical_Range) + " " + str(Vertical_Offset)

        self.client.send_message(message)

        time.sleep(0.8)

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

    def Configure_Timebase(self, Timebase: float, Offset: float):

        """
        - 使用 Configure_Timebase 方法与服务器进行通信
        - 返回值:
        - 若通信成功返回 True，否则返回 False

                - Timebase        时间基准
                - Offset          时间偏移

            - Configure_Timebase(0.005,0)
            - 5ms,0ms偏移
        """
        command = "Configure_Timebase"
        if not self.is_initialized:
            return False
        message = command + " " + str(Timebase) + " " + str(Offset)

        self.client.send_message(message)

        time.sleep(0.2)

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

    def Configure_Trigger_Sweep(self, Trigger_Type: int, Trigger_Sweep_Type: int):

        """
        - 使用 Configure_Trigger_Sweep 方法与服务器进行通信
        - 返回值:
        - 若通信成功返回 True，否则返回 False

                - Trigger_Type                  0：Edge;1：Pulse;2：Video;3：Pattern;4：Duration
                - Trigger_Sweep_Type            0：Auto;1：Normal;2：Single

            - Configure_Trigger_Sweep(0,2)
        """
        command = "Configure_Trigger_Sweep"
        if not self.is_initialized:
            return False
        message = command + " " + str(Trigger_Type) + " " + str(Trigger_Sweep_Type)

        self.client.send_message(message)

        time.sleep(0)

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

    def Configure_Trigger_Edge(self, channel: int, Trigger_Level: float, Trigger_Slope: int):

        """
        - 使用 Configure_Trigger_Edge 方法与服务器进行通信
        - 返回值:
        - 若通信成功返回 True，否则返回 False

                - channel                       通道
                - Trigger_Level
                - Trigger_Slope                 0：Positive;1：Negative;2：Alternation

            - Configure_Trigger_Edge(1,0.5,0)
            - 通道1,0.5V的变化，正向变化
        """
        command = "Configure_Trigger_Edge"
        if not self.is_initialized:
            return False
        message = command + " " + str(channel) + " " + str(Trigger_Level) + " " + str(Trigger_Slope)

        self.client.send_message(message)

        time.sleep(0.6)

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

    def Configure_Trigger_Pulse(self, channel: int, Trigger_Level: float, Trigger_Pulse_Mode: int, Pulse_Width: float):

        """
        - 使用 Configure_Trigger_Edge 方法与服务器进行通信
        - 返回值:
        - 若通信成功返回 True，否则返回 False

                - channel                       通道
                - Trigger_Level
                - Trigger_Pulse_Mode            0：>;1：<;2：=;3:>=;4:<=;5:!=
                - Pulse_Width
            - Configure_Trigger_Pulse(1,0.5,0,0.000001)
            - 通道1,0.5V的变化，大于0.5V的变化，脉冲宽度1us
        """
        command = "Configure_Trigger_Pulse"
        if not self.is_initialized:
            return False
        message = command + " " + str(channel) + " " + str(Trigger_Level) + " " + str(Trigger_Pulse_Mode) + " " + str(
            Pulse_Width)

        self.client.send_message(message)

        time.sleep(0.8)

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

    def ReadWaces(self, channel: list, Timeout: int, WaveDataPath: str, WaveImagePath: str):

        """
        - 使用 ReadWaces 方法与服务器进行通信
        - 返回值:
        - 若通信成功返回 True，否则返回 False

                - channel                       通道
                - Timeout                       超时ms
                - WaveDataPath                  波形数据保存路径
                - WaveImagePath                 波形图像保存路径
            - ReadWaces([1],10000,”“,"")
            - 通道1,超时10s,路径(路径为空或非法时不保存数据)
        """
        command = "ReadWaces"
        if not self.is_initialized:
            return False
        message = command + " " + ','.join(str(x) for x in channel) + " " + str(
            Timeout) + " " + WaveDataPath + " " + WaveImagePath

        self.client.send_message(message)

        time.sleep(2 + 0.8 * len(channel))

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

    def Measurement(self, channel: int, MeasurementFunction: int):

        """
        - 使用 ReadWaces 方法与服务器进行通信
        - 返回值:
        - 若通信成功返回 True，否则返回 False

                - channel                       通道
                - MeasurementFunction           计算函数
                    -0:Voltage Vpp
                    -1:Voltage Max
                    -2:Voltage Min
                    -3:Amplitude
                    -4:Voltage TOP
                    -5:Voltage Base
                    -6:Voltage Average
                    -7:Voltage RMS
                    -8:Overshoot
                    -9:Preshoot
                    -10:Frequency
                    -11:Rise Time
                    -12:Fall Time
                    -13:Period
                    -14:Positive Width
                    -15:Negative Width
                    -16:Positive Duty
                    -17:Negative Duty
            - ReadWaces(1,1)
            - 通道1,计算vppMax
        """
        command = "Measurement"
        MeaData = -9999
        if not self.is_initialized:
            return MeaData
        message = command + " " + str(channel) + " " + str(MeasurementFunction)

        self.client.send_message(message)

        time.sleep(2)

        response = self.client.receive_message()
        response_mapping = {
            command + " Success": True,
            command + " Fail": False,
        }
        if response.startswith(command + " Success"):

            MeaData = float(response.split(" ")[-1])
        else:
            print("非正常通讯返回")
        return MeaData

    def AutoSet(self):

        command = "AutoSet"

        if not self.is_initialized:
            return False
        message = command

        self.client.send_message(message)

        time.sleep(3)

        response = self.client.receive_message()
        print(response)
        response_mapping = {
            command + " Success": True,
            command + " Fail": False,
        }
        if response in response_mapping:
            return response_mapping[response]

        else:
            print("非正常通讯返回")
        return False
