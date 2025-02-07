import pyvisa
import time

class PPH1503D:
    ConstRange5mA = "0.005"
    ConstRange500mA = "0.5"
    ConstRange5A = "5"
    ConstRangeAuto="AUTO"

    def __init__(self, resource_name="172.16.198.51", NohaveInstrument=False,InstrumentName="PPH1503D"):
        """
        初始化 Keysight 34465A 数字万用表。

        :param resource_name: VISA 资源名称，例如 'USB0::0x2A8D::0x0101::MYXXXXXXXX::INSTR'
        """
        self.NohaveInstrument = NohaveInstrument # 用于标识是否有仪器连接
        self.InstrumentName = InstrumentName

        port=1026
        resource_address = f"TCPIP::{resource_name}::{port}::SOCKET"
        self.rm = pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(resource_address)
        self.instrument.timeout = 5000  # 设置超时时间为 5000ms

        # 设置读取和写入的终止符，通常 SCPI over TCP 使用换行符作为终止符
        self.instrument.read_termination = '\n'
        self.instrument.write_termination = '\n'
        time.sleep(0.1)
        self.instrument.write("*RST")
        time.sleep(0.1)
        self.instrument.write(f":ROUT:TERM REAR")
        time.sleep(0.1)

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

    def configure_ON(self, channel):
        """
        Set channel as on。
        :param channel 1/2。
        """
        if self.NohaveInstrument:
            return
        
        if channel == 1:
            self.instrument.write(":OUTP1:STAT ON")
        elif channel == 2:
            self.instrument.write(":OUTP2:STAT ON")
        time.sleep(0.1)

    def configure_OFF(self, channel):
        """
        Set channel as on。
        :param channel 1/2。
        """
        if self.NohaveInstrument:
            return
        
        if channel == 1:
            self.instrument.write(":OUTP1:STAT OFF")
        elif channel == 2:
            self.instrument.write(":OUTP2:STAT OFF")
        time.sleep(0.1)

    def PPH103GetCurrent(self, channel):
        """
        get the channel current。

        :param channel: 1/2。
        :return: 返回当前通道的电流值。
        """
        if self.NohaveInstrument:
            return f"No have instrument {self.InstrumentName}"
        
        if channel == 1:
            respond= float(self.instrument.query(":SENS1:FUNC CURR"))
        elif channel == 2:
            respond= float(self.instrument.query(":SENS2:FUNC CURR"))
        time.sleep(0.1)
        return respond
        

    def PPH103SetVoltage(self,channel, floatVoltage):
        """
        set voltage。
        :param channel: 1/2。"""
        if self.NohaveInstrument:
            return
        
        if channel == 1:
            strcmd=f":SOUR1:VOLT {floatVoltage}"
            #self.instrument.write(":SOUR1:VOLT " + strVoltage)
        elif channel == 2:
            strcmd = f":SOUR2:VOLT {floatVoltage}"
            #self.instrument.write(":SOUR2:VOLT " + strVoltage)
        self.instrument.write(strcmd)
        time.sleep(0.1)

    def PPH103SetLimitCurrent(self,channel, LimitCurrent:float):
        """
        set the current limit。

        :param channel: 1/2。
        """
        if self.NohaveInstrument:
            return
        
        if channel == 1:
            strcmd = f":SOUR1:CURR:LIM {LimitCurrent}"
            #self.instrument.write(":SOUR1:CURR:LIM " + strLimitCurrent)
        elif channel == 2:
            strcmd = f":SOUR1:CURR:LIM {LimitCurrent}"
            #self.instrument.write(":SOUR2:CURR:LIM " + strLimitCurrent)
        self.instrument.write(strcmd)
        time.sleep(0.1)

    def PPH103GetONOFFStatus(self, channel):
        """
        配置触发源和触发延迟。

        :param channel: 1/2。
        """
        if self.NohaveInstrument:
            return
        
        if channel == 1:
            respond= float(self.instrument.query("::OUTP1:STAT?"))
        elif channel == 2:
            respond= float(self.instrument.query("::OUT21:STAT?"))
        time.sleep(0.1)
        return respond

    def PPH103SetCurrentRange(self,channel, range):
        """
        读取测量值。

        :param channel: 1/2。
        :param strRange: ConstRange5mA, ConstRange500mA, ConstRange5A。
        """
        if self.NohaveInstrument:
            return
        
        if channel == 1:
            if range == self.ConstRange5mA:
                str_range = "0.005"
                str_cmd = ":SENS1:CURR:DC:RANG:UPP "+str_range
            elif range == self.ConstRange500mA:
                str_range = "0.5"
                str_cmd = ":SENS1:CURR:DC:RANG:UPP "+str_range
            elif range == self.ConstRange5A:
                str_range = "5"
                str_cmd = ":SENS1:CURR:DC:RANG:UPP "+str_range                
            elif range == self.ConstRangeAuto:
                str_cmd = ":SENS1:CURR:RANG:AUTO ON"
        elif channel == 2:
            if range == self.ConstRange5mA:
                str_range = "MIN"
                str_cmd = ":SENS2:CURR:DC:RANG "+str_range
            elif range == self.ConstRangeAuto:
                str_cmd = ":SENS2:CURR:RANG:AUTO ON"
            else:    
                str_range = "MAX"
                str_cmd = ":SENS2:CURR:DC:RANG "+str_range
        self.instrument.write(str_cmd)

    def close(self):
        """
        关闭与设备的连接。
        """
        self.instrument.close()
        self.rm.close()