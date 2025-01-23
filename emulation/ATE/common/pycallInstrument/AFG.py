from common.pycallInstrument.TCPClient import TCPClient
import time


class CallAFG:
    def __init__(self, AFGNO: int):
        """
        - 初始化 CallAFG 类
        - 参数:
        - AFGNO: 任意函数发生器编号
        """
        instrumentName = "AFG" + str(AFGNO)
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
            time.sleep(1.3)
        time.sleep(1)

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

    def Configure_Standard_Waveform(self, channel: int, Waveform_Function: int, Frequency: float, Amplitude: float,
                                    DC_Offset: float):

        """
        - 使用 Configure_Standard_Waveform 方法与服务器进行通信
        - 返回值:
        - 若通信成功返回 True，否则返回 False
                - channel                    通道
                - Waveform_Function          0：Sine;1：Square;2：Pulse;3：Ramp;4：Noise;5：DC;6：Sin(x)/x;7：Gaussian;8：Lorentz;9：Exponential Rise;10：Exponential Decay;11：Haversine
                - Frequency                  频率
                - Amplitude                  垂直范围
                - DC_Offset                  垂直偏移
            - 适用于Sine, Square,Pulse,Ramp(频率不可超过800KHZ),Noise,DC
            - Configure_Standard_Waveform(1,0,1000000,1,0.2)
            - 通道1(TEKTRONIX,AFG3105只有通道1),正弦波,频率:1MHZ,Y轴上下限长度为1,Y轴偏移0.2(即Y轴坐标为-0.3V至0.7V)

            - 可另外设置占空比，上升和下降时间

            - Noise,DC不支持Burst
        """
        command = "Configure_Standard_Waveform"
        if not self.is_initialized:
            return False
        message = command + " " + str(channel) + " " + str(Waveform_Function) + " " + str(Frequency) + " " + str(
            Amplitude) + " " + str(DC_Offset)

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

    def Configure_Trigger(self, Trigger_Source: int, External_Trigger_Slope: int, Internal_Trigger_Rate: float):

        """
        - 使用 Configure_Trigger 方法与服务器进行通信
        - 返回值:
        - 若通信成功返回 True，否则返回 False

                - Trigger_Source                0:Internal,1:External
                - External_Trigger_Slope        0:Positive,1:Positive
                - Internal_Trigger_Rate(ms)

            - Configure_Trigger(1,0,1)
            - 目前使用均为内部触发，仅修改Internal_Trigger_Rate内部触发时间即可
        """
        command = "Configure_Trigger"
        if not self.is_initialized:
            return False
        message = command + " " + str(Trigger_Source) + " " + str(External_Trigger_Slope) + " " + str(
            Internal_Trigger_Rate)

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

    def Configure_Burst(self, channel: int, Burst_Mode: int, Burst_Count: int, Burst_Delay: float):

        """
        - 使用 Configure_Burst 方法与服务器进行通信
        - 返回值:
        - 若通信成功返回 True，否则返回 False

                - channel                       通道
                - Burst_Mode                    0：Triggered;1：Gated
                - Burst_Count(5)                触发次数
                - Burst_Delay(ns)               触发间隔

            - Configure_Burst(1,0,5,0)
            - 通道1,触发,5次触发，延时0ns

            - Noise,DC不支持Burst
        """
        command = "Configure_Burst"
        if not self.is_initialized:
            return False
        message = command + " " + str(channel) + " " + str(Burst_Mode) + " " + str(Burst_Count) + " " + str(Burst_Delay)

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

    def Configure_Pulse_Waveform(self, channel: int, Duty_Cycle: int, Leading_Edge_Time: int, Trailing_Edge_Time: int,
                                 Delay: int):

        """
        - 使用 Configure_Pulse_Waveform 方法与服务器进行通信
        - 返回值:
        - 若通信成功返回 True，否则返回 False

                - channel                               通道
                - Duty_Cycle                            占空比%
                - Leading_Edge_Time(ns)                 上升时间
                - Trailing_Edge_Time (ns)               下降时间
                - Delay(ns)                             波形开始延时ns

            - Configure_Pulse_Waveform(1,50,10,10，5)
            - 通道1,50%占空比,上升时间10ns,下降时间10ns，延时5ns后波形产生

            - 用于Pulse模式设置,初始化仪器后默认参数为50%占空比,50ns上升下降时间,0ns延时
        """
        command = "Configure_Pulse_Waveform"
        if not self.is_initialized:
            return False
        message = command + " " + str(channel) + " " + str(Duty_Cycle) + " " + str(Leading_Edge_Time) + " " + str(
            Trailing_Edge_Time) + " " + str(Delay)

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

    def Enable_Output(self, channel: int, Enable_Output: int):

        """
        - 使用 Enable_Output 方法与服务器进行通信
        - 返回值:
        - 若通信成功返回 True，否则返回 False

                - channel                               通道
                - Enable_Output

            - Enable_Output(1,1)
            - 通道1开

        """
        command = "Enable_Output"
        if not self.is_initialized:
            return False
        message = command + " " + str(channel) + " " + str(Enable_Output)

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
