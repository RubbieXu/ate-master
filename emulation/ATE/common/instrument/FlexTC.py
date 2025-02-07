import socket
import time
import math

class FlexTC:
    ERROR_OUT_OF_RANGE_VAL = 998
    FLEXTC_SLOWDOWN_TEMP_DELTA = 15

    FLEXTC_CMD_SET_TEMP = "MI0699,"  # '* + "temp"
    FLEXTC_CMD_QUERY_STATUS = "MB0020?"
    FLEXTC_CMD_QUERY_TEMP = "MI0006?"
    FLEXTC_CMD_OUTPUT_ON = "MB0020,0"
    FLEXTC_CMD_OUTPUT_OFF = "MB0020,1"
    FLEXTC_CMD_RATEACTIVE = "MB0074,1"
    FLEXTC_CMD_RATEVALUE6 = "MI0045,0010"  # default is 6
    FLEXTC_CMD_RATEVALUE4 = "MI0045,0010"  # default is 4

    def __init__(self, resource_name="172.16.198.200", NohaveInstrument=False,InstrumentName="FlexTC"):
        """
        初始化 FlexTC。

        :param resource_name: VISA 资源名称，例如 'USB0::0x2A8D::0x0101::MYXXXXXXXX::INSTR'
        """
        self.NohaveInstrument = NohaveInstrument # 用于标识是否有仪器连接
        self.InstrumentName = InstrumentName

        #port=5000
        #resource_address = f"TCPIP::{resource_name}::{port}::SOCKET"
        #self.rm = pyvisa.ResourceManager()
        #self.instrument = self.rm.open_resource(resource_address)
        #self.instrument.timeout = 5000  # 设置超时时间为 5000ms

        # 设置读取和写入的终止符，通常 SCPI over TCP 使用换行符作为终止符
        #self.instrument.read_termination = '\n'
        #self.instrument.write_termination = '\n'
        time.sleep(0.1)
        #self.instrument.write("*RST")

    def TCReadWrite(self,data):
        if self.NohaveInstrument:
            return f"No have instrument {self.InstrumentName}"
        ip_address = "172.16.198.200"
        port = 5000
        try:
            # 创建一个TCP/IP socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                # 连接到设备
                client_socket.connect((ip_address, port))

                # 将字符串转换为字节数组
                byte_data = data.encode('ascii')

                # 发送数据
                client_socket.sendall(byte_data)
                time.sleep(0.2)

                received_data = client_socket.recv(1024)
                response_data = received_data.decode('ascii')

                # 关闭连接
                client_socket.shutdown(socket.SHUT_RDWR)
                client_socket.close()
                time.sleep(0.1)

                return response_data
        except Exception as ex:
            print(f"Error writing data to device: {ex}")
            return ""

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

    def FlexTC_ON(self):
        """
        Set  on。
        :param channel 1/2。
        """
        if self.NohaveInstrument:
            return
        
        #self.instrument.write(self.FLEXTC_CMD_OUTPUT_ON)
        self.TCReadWrite(self.FLEXTC_CMD_OUTPUT_ON)
        time.sleep(0.1)

    def FlexTC_OFF(self):
        """
        Set  off。
        :param channel 1/2。
        """
        if self.NohaveInstrument:
            return
        
        #self.instrument.write(self.FLEXTC_CMD_OUTPUT_OFF)
        self.TCReadWrite(self.FLEXTC_CMD_OUTPUT_OFF)
        time.sleep(0.1)

    def FlexTC_RateActive(self):
        """
        Set  rateactive。
        :param channel 1/2。
        """
        if self.NohaveInstrument:
            return
        
        #self.instrument.write(self.FLEXTC_CMD_RATEACTIVE)
        self.TCReadWrite(self.FLEXTC_CMD_RATEACTIVE)
        time.sleep(0.1)

    def FlexTC_RateSet6(self):
        """
        Set  rateset6。
        :param channel 1/2。
        """
        if self.NohaveInstrument:
            return
        
        #self.instrument.write(self.FLEXTC_CMD_RATEVALUE6)
        self.TCReadWrite(self.FLEXTC_CMD_RATEVALUE6)
        time.sleep(0.1)

    def FlexTC_RateSet4(self):
        """
        Set  rateset4。
        :param channel 1/2。
        """
        if self.NohaveInstrument:
            return
        
        #self.instrument.write(self.FLEXTC_CMD_RATEVALUE4)
        self.TCReadWrite(self.FLEXTC_CMD_RATEVALUE4)
        time.sleep(0.1)

    def FlexTC_SetTemp(self, dbl_temp_setpoint:float):
        """
        Set  temperature。
        :param dbl_temp_setpoint float。
        """
        self.FlexTC_RateSet6()
        self.FlexTC_RateActive()
        self.FlexTC_ON()

        if (dbl_temp_setpoint >= 0):
            int_value_temp = math.floor(dbl_temp_setpoint * 10)
            str_temp = f"{int_value_temp:04d}"
        else:
            int_value_temp = math.floor(dbl_temp_setpoint * 10)
            str_temp = f"{int_value_temp:03d}"

        str_cmd = FlexTC.FLEXTC_CMD_SET_TEMP + str_temp
    
        #self.instrument.write(str_cmd)
        self.TCReadWrite(str_cmd)
        time.sleep(0.1)    

    def Flext_TC_GetTemp(self) -> float:
        """
        Get  temperature。
        :param none
        :return: 返回当前温度值。
        """
        str_cmd = FlexTC.FLEXTC_CMD_QUERY_TEMP        
        #str_val= self.instrument.query(str_cmd)
        str_val= self.TCReadWrite(str_cmd)
        db_actual_temp = self.ERROR_OUT_OF_RANGE_VAL # 默认值
        str_temp = str_val.split(',')
        if len(str_temp) >= 2:
            # 假设数组的第二个元素是所需的值
            db_actual_temp = float(str_temp[1]) / 10.0            
            # 打印结果或根据需要使用它
            print(f"Updated ActualTemp: {db_actual_temp}")
        else:
            print("Invalid input string")

        return db_actual_temp       

    def FlexTC_settle_temp(self,dbl_temp_setpoint: float) -> bool:
        """
        Set  temperature。
        :param dbl_temp_setpoint float。
        :return: 返回是否温度稳定。
        """
        int_iterations = 0
        int_settle_count = 0
        dbl_actual_temp = 0.0
        TIMEOUT = 30  # 30*10s
        is_settle = False  # default is not settle

        # Set the temperature setpoint
        self.FlexTC_SetTemp(dbl_temp_setpoint)
        time.sleep(2)

        # Wait for the temperature to settle for 2 minutes
        dbl_actual_temp = self.Flext_TC_GetTemp()
        int_iterations = 0

        for int_settle_count in range(10):
            # Reset the count if the temperature has not settled into a steady state
            if abs(dbl_actual_temp - dbl_temp_setpoint) > 0.5:
                int_settle_count = -1

            # Wait 10 seconds for the next status update
            time.sleep(10)
            dbl_actual_temp = self.Flext_TC_GetTemp()

            # Exit this loop and use the current temperature if it has not stabilized in over 25 minutes
            int_iterations += 1
            if int_iterations > TIMEOUT:
                break

        if int_iterations > TIMEOUT:
            is_settle = False
        else:
            is_settle = True

        # Return
        return is_settle    
     

    def in_thread_temp_ramp_slowdown(self,dbl_temp_setpoint: float):
        """
        Slowdown  temperature。
        :param dbl_temp_setpoint float。
        
        """        
        dbl_temp_diff = self.ERROR_OUT_OF_RANGE_VAL
        dbl_actual_temp = 0.0
        dbl_temp = 0.0
        dbl_temp_diff_in_level = 1.0  # 1.0 C
        is_down = False

        # Wait for the temperature to stabilize
        while abs(dbl_temp_diff) > FlexTC.FLEXTC_SLOWDOWN_TEMP_DELTA:
            dbl_actual_temp = self.Flext_TC_GetTemp()
            dbl_temp_diff = dbl_temp_setpoint - dbl_actual_temp

            if abs(dbl_temp_diff) > FlexTC.FLEXTC_SLOWDOWN_TEMP_DELTA:
                if dbl_temp_diff >= 0:
                    dbl_temp = dbl_actual_temp + FlexTC.FLEXTC_SLOWDOWN_TEMP_DELTA
                    is_down = True
                else:
                    dbl_temp = dbl_actual_temp - FlexTC.FLEXTC_SLOWDOWN_TEMP_DELTA
                    is_down = True

                    if dbl_actual_temp > 30:
                        self.FlexTC_RateSet4()

                self.FlexTC_SetTemp(dbl_temp)

                # the max is 180s=3*50 for 15 C
                for _ in range(150):
                    time.sleep(3)
                    # the below sleep then read temperature is for display the temperature in the UI
                    dbl_actual_temp = self.Flext_TC_GetTemp()
                    if abs(dbl_temp - dbl_actual_temp) < dbl_temp_diff_in_level:
                        if is_down:
                            time.sleep(2)
                        else:
                            time.sleep(2)
                        break
        self.FlexTC_settle_temp(dbl_temp_setpoint)     

    def close(self):
        """
        关闭与设备的连接。
        """
        self.instrument.close()
        self.rm.close()