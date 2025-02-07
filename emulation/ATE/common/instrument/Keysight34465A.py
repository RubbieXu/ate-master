import pyvisa
import time

class Keysight34465A:
    def __init__(self, resource_name,NohaveInstrument=False,InstrumentName="Keysight34465A"):
        """
        初始化 Keysight 34465A 数字万用表。

        :param resource_name: VISA 资源名称，例如 'USB0::0x2A8D::0x0101::MYXXXXXXXX::INSTR'
        """
        self.NohaveInstrument = NohaveInstrument # 用于标识是否有仪器连接
        self.InstrumentName = InstrumentName
        self.rm = pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(resource_name)
        self.instrument.timeout = 5000  # 设置超时时间为 5000ms

    def get_identity(self):
        """
        获取设备标识信息。
        :return: 返回设备的 IDN 信息。
        """
        if self.NohaveInstrument:
            return f"No have instrument {self.InstrumentName}"
        
        respond= self.instrument.query("*IDN?")   
        time.sleep(0.1)     
        return respond

    def reset(self):
        """
        复位设备。
        """
        if self.NohaveInstrument:
            return 
        
        self.instrument.write("*RST")
        time.sleep(0.1)

    def configure_voltage_dc(self, range_value:float):
        """
        配置直流电压测量模式。

        :param range_value: 量程范围（单位：V），默认为 10V。
        :param resolution: 分辨率（单位：V），默认为 0.001V。
        """
        if self.NohaveInstrument:
            return 
        
        self.instrument.write(f"CONF:VOLT:DC {range_value}")
        time.sleep(0.1)
        self.instrument.write(f"SENS:VOLT:DC:NPLC 10")
        time.sleep(0.1)

    def configure_current_dc(self, range_value:float):
        """
        配置直流电压测量模式。

        :param range_value: 量程范围（单位：V），默认为 10V。
        :param resolution: 分辨率（单位：V），默认为 0.001V。
        """
        if self.NohaveInstrument:
            return 
                
        self.instrument.write(f"CONF:CURR:DC {range_value}")
        time.sleep(0.1)
        self.instrument.write(f"SENS:CURR:DC:NPLC 10")
        time.sleep(0.1)

    def measure_voltage_dc(self):
        """
        测量直流电压。
        :return: 返回测量的电压值（单位：V）。
        """
        if self.NohaveInstrument:
            return f"No have instrument {self.InstrumentName}"
        
        respond= float(self.instrument.query("READ?"))
        time.sleep(0.1)     
        return respond

    def measure_current_dc(self):
        """
        测量直流电压。

        :return: 返回测量的电压值（单位：V）。
        """
        if self.NohaveInstrument:
            return f"No have instrument {self.InstrumentName}"
                
        respond= float(self.instrument.query("READ?"))
        time.sleep(0.1)     
        return respond

    def close(self):
        """
        关闭与设备的连接。
        """
        self.instrument.close()
        self.rm.close()