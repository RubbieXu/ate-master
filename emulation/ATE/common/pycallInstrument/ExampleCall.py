import time
import datetime
from common.pycallInstrument.OSC import CallOSC
from common.pycallInstrument.AFG import CallAFG
from common.pycallInstrument.DMM import CallDMM
from common.pycallInstrument.DCPwr import CallDCPwr
from common.pycallInstrument.LA_KingstVis import CallLA_KingstVis
import getpass
import pygetwindow as gw

# # KingstVis使用范例：
# try:
#
#     Kingst1 = CallLA_KingstVis(1)
#
#     for i in range(1):
#         try:
#             Kingst1.Configure(1.65, 100000000, 100000000, 1)
#             Kingst1.Start()
#             time.sleep(1.5)
#             Kingst1.SaveData("D:\data03.kvdat")
#             # Kingst1.SaveData("D:\\test.txt")
#         except Exception as e:
#             print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}: 通信发生错误：{str(e)}")
#
#     Kingst1.closeTCP()  # 关闭TCP客户端
#
# except Exception as e:
#     print(f"通信发生错误：{str(e)}")


# #直流电源使用范例：
# try:
#
#     DCPwr1 = CallDCPwr(1)                               #打开TCP客户端，接入仪器控制程序
#
#
#     for i in range(1):
#         try:
#             DCPwr1.openInstr(1)                       #打开仪器,初始化
#             DCPwr1.Configure(0,1)                     #通道1,电压输出,1V
#             DCPwr1.Enable_Output(1)                   #输出on
#             Data=DCPwr1.ReadData()                    #获取电压电流
#             DCPwr1.Enable_Output(0)
#             DCPwr1.closeInstr()                       #仪器串口关闭
#
#         except Exception as e:
#             print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}: 通信发生错误：{str(e)}")
#
#
#     DCPwr1.closeTCP()                                 #关闭TCP客户端
#
# except Exception as e:
#     print(f"通信发生错误：{str(e)}")


# # 数字万用表使用范例：
# try:
#
#     DMM1 = CallDMM(1)  # 打开TCP客户端，接入仪器控制程序
#
#     for i in range(1):
#         try:
#             DMM1.openInstr()  # 打开仪器,初始化
#             # DMM1.Configure_Channel(1, b'0', b'0')
#             DMM1.Configure_Channel(1, 0, 0)  # 通道1,DC模式,量程±50mV
#             for j in range(10):
#                 Data = DMM1.ReadData()
#                 print(Data)
#             DMM1.closeInstr()  # 仪器串口关闭
#
#         except Exception as e:
#             print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}: 通信发生错误：{str(e)}")
#
#     DMM1.closeTCP()  # 关闭TCP客户端
#
# except Exception as e:
#     print(f"通信发生错误：{str(e)}")

# # 任意函数发生器使用范例：
# try:
#
#     AFG1 = CallAFG(1)  # 打开TCP客户端，接入仪器控制程序
#
#     for i in range(1):
#         try:
#             AFG1.openInstr(1)  # 打开仪器,初始化
#             AFG1.Configure_Standard_Waveform(1, 0, 10, 5,
#                                              0)  # 通道1(TEKTRONIX,AFG3105只有通道1),正弦波,频率:1MHZ,Y轴上下限长度为1,Y轴偏移0.2(即Y轴坐标为-0.3V至0.7V)
#             AFG1.Configure_Trigger(0, 0, 1000)  # 设置内部触发，触发时间1ms
#             AFG1.Configure_Burst(1, 0, 5, 10)  # 通道1,触发,5次触发，延时0ns
#             AFG1.Configure_Pulse_Waveform(1, 50, 10, 10, 100)  # 通道1,50%占空比,上升时间10ns,下降时间10ns，延时5ns后波形产生
#             AFG1.Enable_Output(1, 1)
#             time.sleep(0.5)
#             AFG1.Enable_Output(1, 0)
#             AFG1.closeInstr()  # 仪器串口关闭
#
#         except Exception as e:
#             print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}: 通信发生错误：{str(e)}")
#
#     AFG1.closeTCP()  # 关闭TCP客户端
#
# except Exception as e:
#     print(f"通信发生错误：{str(e)}")

# def OSC_control():
#     # 示波器使用范例：
#     try:
#
#         OSC1 = CallOSC(1)  # 打开TCP客户端，接入仪器控制程序
#
#         for i in range(1):
#             try:
#                 OSC1.openInstr(0)
#                 OSC1.Configure_Trigger_Sweep(0, 2)
#                 # OSC1.Configure_Channel(1,0,10,5,0)
#                 # OSC1.Configure_Timebase(0.0005,0)
#
#                 # OSC1.Configure_Trigger_Pulse(1,14.5,0,0.000001)
#                 OSC1.AutoSet()
#                 OSC1.ReadWaces([1], 10000, "D:\\test.bmp", "D:\\test.csv")
#                 MeaData = OSC1.Measurement(1, 1)
#                 print(MeaData)
#                 OSC1.closeInstr()  # 仪器串口关闭
#
#             except Exception as e:
#                 print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}: 通信发生错误：{str(e)}")
#         OSC1.closeTCP()  # 关闭TCP客户端
#
#     except Exception as e:
#         print(f"通信发生错误：{str(e)}")

#
# OSC1.openInstr(0)
#             # OSC1.Configure_Channel(1,0,1.0,0.50,0.1)
#             # OSC1.Configure_Timebase(0.005,0)
#             # OSC1.Configure_Trigger_Sweep(0,2)
#             # OSC1.Configure_Trigger_Edge(1,0.1,2)
#             OSC1.AutoSet()
#             # MeaData = OSC1.Measurement(1, 1)
#             # print(MeaData)
#             #
#             OSC1.ReadWaces([1], 10000, "D:\\test.bmp", "D:\\test.csv")
#             OSC1.closeInstr()                                           #仪器串口关闭
