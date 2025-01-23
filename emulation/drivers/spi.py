import ch347
import ctypes
import time

class spi:
    # spi parameter
    device_index = 0  # Set the device index according to your requirements
    iIndex = 0 # Set the device index
    cs_continuous_en = 0

    config = ch347.mSpiCfgS()
    config.iMode = 0x00    # 0-3:SPI Mode0/1/2/3
    config.iClock = 0x6   # 0=60MHz, 1=30MHz, 2=15MHz, 3=7.5MHz, 4=3.75MHz, 5=1.875MHz, 6=937.5KHz，7=468.75KHz
    config.iByteOrder = 1 # 0=低位在前(LSB), 1=高位在前(MSB)
    config.iSpiWriteReadInterval = 0
    config.iSpiOutDefaultData = 0
    config.iChipSelect = (1<<7 | 0) # 片选控制, 位7为0则忽略片选控制, 位7为1则参数有效: 位1位0为00/01分别选择CS1/CS2引脚作为低电平有效片选
    config.CS1Polarity = 0
    config.CS2Polarity = 0
    config.iIsAutoDeativeCS = 1
    config.iActiveDelay = 50
    config.iDelayDeactive = 50

    # gpio parameter
    pin0 =  1<<0
    pin1 =  1<<1
    pin2 =  1<<2
    pin3 =  1<<3
    pin4 =  1<<4
    pin5 =  1<<5
    pin6 =  1<<6
    pin7 =  1<<7

    def __init__(self):
        # open the device
        result = ch347.OpenDevice(self.device_index)
        if result:
            print(f"Opened device Successfully, index: {self.device_index}")
        else:
            print(f"Open device failed, close device index: {self.device_index}")
            self.deinit()

        # set timeout 500ms
        ch347.SetTimeout(self.device_index, 50000, 50000)

        # get device information
        self.get_device_information()
        # spi init
        result = ch347.SPI_Init(self.device_index, self.config)
        if result:
            print(f"Init successfully, index: {self.device_index}")
        else:
            print(f"Init failed, result: {result}, close device index: {self.device_index}")
        # get spi configuration
        self.get_config()

        # gpio init
        # IO 3 set to output
        ch347.GPIO_SetValue(self.iIndex, self.pin3, self.pin3, self.pin3)   # test_rst: output, high level
        # IO 5 set to output
        ch347.GPIO_SetValue(self.iIndex, self.pin5, self.pin5, self.pin5)   # test_mode: output, high level(enable test mode)
        # IO 6 set to input
        ch347.GPIO_SetValue(self.iIndex, self.pin6, 0x00, 0x00)   # test_bist_done
        # IO 7 set to input
        ch347.GPIO_SetValue(self.iIndex, self.pin7, 0x00, 0x00) # test_bist_success

    def deinit(self):
        # IO 3 set to output
        ch347.GPIO_SetValue(self.iIndex, self.pin3, self.pin3, 0x00)   # test_rst: output, low level
        # IO 5 set to output
        ch347.GPIO_SetValue(self.iIndex, self.pin5, self.pin5, self.pin5)   # test_mode: output, high level(enable test mode)

        # Example usage of CH347CloseDevice
        result = ch347.CloseDevice(self.device_index)
        if result:
            print(f"Successfully closed device index: {self.device_index}")
        else:
            print(f"Failed to close device index: {self.device_index}")

    def write_read(self, buffer:list, length:int):
        data = (ch347.spi_buffer)()

        # write and read data
        if self.cs_continuous_en:
            # copy buffer to data
            for i in range(0, length):
                data.filed[i] = buffer[i]
                buffer[i] = 0x00  # clear buffer
            ch347.SPI_WriteRead(self.iIndex, self.config.iChipSelect, length, data)
            # save rx data to buffer
            for i in range(0, length):
                buffer[i] = data.filed[i]
        else:
            for i in range(0, length):
                data.filed[0] = buffer[i] # copy buffer to data
                buffer[i] = 0x00  # clear buffer
                ch347.SPI_WriteRead(self.iIndex, self.config.iChipSelect, 1, data)
                buffer[i] = data.filed[0] # save rx data to buffer

    def get_device_information(self):
        # Example usage of CH347GetDeviceInfor
        result, device_info = ch347.GetDeviceInfor(self.device_index)
        if result:
            print("Device Information:")
            print(f"iIndex: {device_info.iIndex}")
            print(f"DevicePath: {device_info.DevicePath.decode()}")
            print(f"UsbClass: {device_info.UsbClass}")
            print(f"FuncType: {device_info.FuncType}")
            print(f"DeviceID: {device_info.DeviceID.decode()}")
            print(f"ChipMode: {device_info.ChipMode}")
            print(f"DevHandle: {device_info.DevHandle}")
            print(f"BulkOutEndpMaxSize: {device_info.BulkOutEndpMaxSize}")
            print(f"BulkInEndpMaxSize: {device_info.BulkInEndpMaxSize}")
            print(f"UsbSpeedType: {device_info.UsbSpeedType}")
            print(f"CH347IfNum: {device_info.CH347IfNum}")
            print(f"DataUpEndp: {device_info.DataUpEndp}")
            print(f"DataDnEndp: {device_info.DataDnEndp}")
            print(f"ProductString: {device_info.ProductString.decode()}")
            print(f"ManufacturerString: {device_info.ManufacturerString.decode()}")
            print(f"WriteTimeout: {device_info.WriteTimeout}")
            print(f"ReadTimeout: {device_info.ReadTimeout}")
            print(f"FuncDescStr: {device_info.FuncDescStr.decode()}")
            print(f"FirewareVer: {device_info.FirewareVer}")
            print(repr(device_info))
        else:
            print("Failed to get device information.")

        # Example usage of CH347GetVersion
        result, driver_ver, dll_ver, device_ver, chip_type = ch347.GetVersion(self.device_index)
        if result:
            print("Version Information:")
            print(f"Driver Version: {driver_ver}")
            print(f"DLL Version: {dll_ver}")
            print(f"Device Version: {device_ver}")
            print(f"Chip Type: {chip_type}")
        else:
            print("Failed to get version information.")

    def get_config(self):
        result,cfg = ch347.SPI_GetCfg(self.iIndex)
        if result:
            print(f"SPI mode: {cfg.iMode}")
            print(f"SPI iClock: {cfg.iClock}")
            print(f"SPI iByteOrder: {cfg.iByteOrder}")
            print(f"SPI iSpiWriteReadInterval: {cfg.iSpiWriteReadInterval}")
            print(f"SPI iSpiOutDefaultData: {cfg.iSpiOutDefaultData}")
            print(f"SPI iChipSelect: {cfg.iChipSelect}")
            print(f"SPI CS1Polarity: {cfg.CS1Polarity}")
            print(f"SPI CS2Polarity: {cfg.CS2Polarity}")
            print(f"SPI iIsAutoDeativeCS: {cfg.iIsAutoDeativeCS}")
            print(f"SPI iActiveDelay: {cfg.iActiveDelay}")
            print(f"SPI iDelayDeactive: {cfg.iDelayDeactive}")
        else:
            print(f"result: {result}")
            print("SPI get cfg failed.")

    def set_config(self, iClock = 0x3):
         #clock: 0=60MHz, 1=30MHz, 2=15MHz, 3=7.5MHz, 4=3.75MHz, 5=1.875MHz, 6=937.5KHz，7=468.75KHz
        self.config.iClock = iClock
        result = ch347.SPI_Init(self.device_index, self.config)
        if result:
            print(f"ReInit successfully, index: {self.device_index}")
        else:
            print(f"ReInit failed, result: {result}, close device index: {self.device_index}")


    def set_pin_rst(self, level: bool): # pin3
        if (level == True):
            ch347.GPIO_SetValue(self.iIndex, self.pin3, self.pin3, self.pin3)   # test_rst_n
        else:
            ch347.GPIO_SetValue(self.iIndex, self.pin3, self.pin3, 0x00)

    def set_pin_stRst(self, level: bool): # pin5
        if (level == True):
            ch347.GPIO_SetValue(self.iIndex, self.pin5, self.pin5, self.pin5)   # stm32 reset
        else:
            ch347.GPIO_SetValue(self.iIndex, self.pin5, self.pin5, 0x00)

    # def set_pin_adc1RegTrg(self, level: bool): # pin1
    #     if (level == True):
    #         ch347.GPIO_SetValue(self.iIndex, self.pin1, self.pin1, self.pin1)
    #     else:
    #         ch347.GPIO_SetValue(self.iIndex, self.pin1, self.pin1, 0x00)

    # def set_pin_adc2RegTrg(self, level: bool): # pin4
    #     if (level == True):
    #         ch347.GPIO_SetValue(self.iIndex, self.pin4, self.pin4, self.pin4)
    #     else:
    #         ch347.GPIO_SetValue(self.iIndex, self.pin4, self.pin4, 0x00)

    def set_pin_adcRegTrg(self, level: bool): # pin6
        if (level == True):
            ch347.GPIO_SetValue(self.iIndex, self.pin6, self.pin6, self.pin6)
        else:
            ch347.GPIO_SetValue(self.iIndex, self.pin6, self.pin6, 0x00)

    def set_pin_adcInjTrg(self, level: bool): # pin7
        if (level == True):
            ch347.GPIO_SetValue(self.iIndex, self.pin7, self.pin7, self.pin7)
        else:
            ch347.GPIO_SetValue(self.iIndex, self.pin7, self.pin7, 0x00)

