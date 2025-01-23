import os
import ctypes

class spi_base:
    def __init__(self):
        pass
    def deinit(self):
        pass
    def write_read(self, buffer:list, length:int):
        pass
    def get_device_information(self):
        pass
    def get_config(self):
        pass
    def set_pin_rst(self, level: bool): # pin3
        pass
    def set_pin_stRst(self, level: bool): # pin5
        pass
    def get_pin_bist_done(self) -> bool:  # pin6
        pass
    def get_pin_bist_success(self) -> bool: # pin7
        pass


class spi(spi_base):
    '''
        specific to the protocol that are implemented in the chip
        BIT1-0=CPOL-CPHA:	00 - MODE0 - data captured on rising edge, propagated on falling
                            01 - MODE1 - data captured on falling edge, propagated on rising
                            10 - MODE2 - data captured on falling edge, propagated on rising
                            11 - MODE3 - data captured on rising edge, propagated on falling
        BIT4-BIT2: 000 - A/B/C/D_DBUS3=ChipSelect
                         : 001 - A/B/C/D_DBUS4=ChipSelect
                         : 010 - A/B/C/D_DBUS5=ChipSelect
                         : 011 - A/B/C/D_DBUS6=ChipSelect
                         : 100 - A/B/C/D_DBUS7=ChipSelect
        BIT5: ChipSelect is active high if this bit is 0
        BIT6 -BIT31		: Reserved
        */
    '''
    SPI_CONFIG_OPTION_MODE0 = 0x00
    SPI_CONFIG_OPTION_MODE1 = 0x01
    SPI_CONFIG_OPTION_MODE2 = 0x02
    SPI_CONFIG_OPTION_MODE3 = 0x03

    SPI_CONFIG_OPTION_CS_DBUS3 = 0x00
    SPI_CONFIG_OPTION_CS_DBUS4 = 0x04
    SPI_CONFIG_OPTION_CS_DBUS5 = 0x08
    SPI_CONFIG_OPTION_CS_DBUS6 = 0x0C
    SPI_CONFIG_OPTION_CS_DBUS7 = 0x10

    SPI_CONFIG_OPTION_CS_ACTIVEHIGH = 0x00
    SPI_CONFIG_OPTION_CS_ACTIVELOW = 0x20

    # /* transferOptions-Bit0: If this bit is 0 then it means that the transfer size provided is in bytes */
    SPI_TRANSFER_OPTIONS_SIZE_IN_BYTES = 0x00
    # /* transferOptions-Bit0: If this bit is 1 then it means that the transfer size provided is in bytes */
    SPI_TRANSFER_OPTIONS_SIZE_IN_BITS = 0x01
    # transferOptions-Bit1: if BIT1 is 1 then CHIP_SELECT line will be enabled at start of transfer */
    SPI_TRANSFER_OPTIONS_CHIPSELECT_ENABLE = 0x02
    # transferOptions-Bit2: if BIT2 is 1 then CHIP_SELECT line will be disabled at end of transfer */
    SPI_TRANSFER_OPTIONS_CHIPSELECT_DISABLE = 0x04
    # transferOptions-Bit3: if BIT3 is 1 then LSB will be processed first */
    SPI_TRANSFER_OPTIONS_LSB_FIRST = 0x08

    # Default Option
    SPI_TRANSFER_OPTIONS_DEFAULT = SPI_TRANSFER_OPTIONS_SIZE_IN_BYTES + \
        SPI_TRANSFER_OPTIONS_CHIPSELECT_ENABLE + \
        SPI_TRANSFER_OPTIONS_CHIPSELECT_DISABLE

    GPIO0 = 0x1
    GPIO1 = 0x2
    GPIO2 = 0x4
    GPIO3 = 0x8
    GPIO4 = 0x10
    GPIO5 = 0x20
    GPIO6 = 0x40
    GPIO7 = 0x80

    class DeviceInfo(ctypes.Structure):
        _fields_ = [
            ('Flags', ctypes.c_ulong),
            ('Type', ctypes.c_ulong),
            ('ID', ctypes.c_ulong),
            ('LocID', ctypes.c_ulong),
            ('SerialNumber', ctypes.c_ubyte*16),
            ('Description', ctypes.c_ubyte*64),
            ('ftHandle', ctypes.c_void_p)]


    class ChannelConfig(ctypes.Structure):
        _fields_ = [("ClockRate", ctypes.c_uint32),
                    ("LatencyTimer", ctypes.c_uint8),
                    ("Options", ctypes.c_uint32),
                    ("Pins", ctypes.c_uint32),
                    ("reserved", ctypes.c_uint16)]
    class SpiError(Exception):
        pass

    def __init__(self, chn_no = 0):

        file_dir = os.path.dirname(__file__)
        work_dir = file_dir + '\..' + '\lib'

        self.dll = ctypes.cdll.LoadLibrary(work_dir  + '\libmpsse.dll')

        self.handle = ctypes.c_void_p()
        self.chn_no = chn_no
        self.gpiodir = 0xff
        self.gpioval = 0xff

        self.clk = 30000000
        self.latency = 0
        self.config = self.SPI_CONFIG_OPTION_CS_ACTIVELOW | self.SPI_CONFIG_OPTION_MODE1 | self.SPI_CONFIG_OPTION_CS_DBUS3
        self.pins = 0xFFFFFFFF

        self.dll.Init_libMPSSE()

        self.gpioinit()
        self.gpioSetDirOutput(0xFF)

        ret = self.dll.SPI_OpenChannel(self.chn_no, ctypes.byref(self.handle))
        if ret:
            raise spi.SpiError(
                "Error: Could not open channel %d ret=%d" % (chn_no, ret))

        chn_conf = self.ChannelConfig(self.clk, self.latency, self.config, self.pins, 0xFFFF)

        ret = self.dll.SPI_InitChannel(self.handle, ctypes.byref(chn_conf))
        if ret:
            raise spi.SpiError(
                "Error: could not initialize channel ret=%d" % ret)

    def deinit(self):
        ret = self.dll.SPI_CloseChannel(self.handle)
        if ret:
            raise spi.SpiError("Error: Could not close channel ret=%d" % ret)

        self.dll.Cleanup_libMPSSE()

    def write_read(self, buffer:list, length:int):
        return self.readWrite(buffer, length)

    def openChannel(self):
        ret = self.dll.SPI_OpenChannel(self.chn_no, ctypes.byref(self.handle))
        if ret:
            raise spi.SpiError(
                "Error: Could not open channel %d ret=%d" % (chn_no, ret))

    def closeChannel(self):
        ret = self.dll.SPI_CloseChannel(self.handle)
        if ret:
            raise spi.SpiError("Error: Could not close channel ret=%d" % ret)

    def get_device_information(self):
        self.getChannelInfo()

    def get_config(self):
        pass

    def set_pin_rst(self, level: bool): # pin3
        if (level == True):
            self.gpioSetValue(self.GPIO3)
        else:
            self.gpioReSetValue(self.GPIO3)
        pass
    def set_pin_mode(self, level: bool): # pin5
        if (level == True):
            self.gpioSetValue(self.GPIO5)
        else:
            self.gpioReSetValue(self.GPIO5)
        pass
    def get_pin_bist_done(self) -> bool:  # pin6
        if (level == True):
            self.gpioSetValue(self.GPIO6)
        else:
            self.gpioReSetValue(self.GPIO6)
        pass
    def get_pin_bist_success(self) -> bool: # pin7
        if (level == True):
            self.gpioSetValue(self.GPIO7)
        else:
            self.gpioReSetValue(self.GPIO7)
        pass

    @staticmethod
    def getNumChannels():
        chn_count = ctypes.c_uint32()

        ret = dll.SPI_GetNumChannels(ctypes.byref(chn_count))
        if ret:
            raise spi.SpiError("Error: getNumChannels ret=%d" % ret)
        return chn_count.value

    @staticmethod
    def getChannelInfo(chn_no):
        dev_info = DeviceInfo()
        ret = dll.SPI_GetChannelInfo(chn_no, ctypes.byref(dev_info))
        if ret:
            raise spi.SpiError("Error: getChannelInfo ret=%d" % ret)

        chn_info = {
            'Flags': dev_info.Flags,
            'Type':  dev_info.Type,
            'ID': dev_info.ID,
            'LocID': dev_info.LocID,
            'SerialNumber': ''.join(map(chr, dev_info.SerialNumber)).split('\x00')[0],
            'Description': ''.join(map(chr, dev_info.Description)).split('\x00')[0]
        }

        return chn_info

    def write(self, write_buffer, size_bytes=None, options=SPI_TRANSFER_OPTIONS_DEFAULT):

        if size_bytes == None:
            size_bytes = len(write_buffer)

        buffer = ctypes.create_string_buffer(size_bytes)

        for i in range(size_bytes):
            buffer[i] = write_buffer[i]

        size_to_transfer = ctypes.c_uint32()
        size_to_transfer.value = size_bytes

        size_transfered = ctypes.c_uint32()

        ret = dll.SPI_Write(
            self.handle,
            buffer,
            size_to_transfer,
            ctypes.byref(size_transfered),
            options
        )

        if ret:
            raise spi.SpiError("Error: read write failed ret=%d" % ret)

        if size_transfered.value != size_to_transfer.value:
            raise spi.SpiError("Error: transfer=%d != transferred=%d",
                               size_to_transfer.value,
                               size_transfered.value)

    def read(self, size_bytes, options=SPI_TRANSFER_OPTIONS_DEFAULT):

        if size_bytes == None:
            size_bytes = len(write_buffer)

        buffer = ctypes.create_string_buffer(size_bytes)

        size_to_transfer = ctypes.c_uint32()
        size_to_transfer.value = size_bytes

        size_transfered = ctypes.c_uint32()

        ret = dll.SPI_Read(
            self.handle,
            buffer,
            size_to_transfer,
            ctypes.byref(size_transfered),
            options
        )

        if ret:
            raise spi.SpiError("Error: read write failed ret=%d" % ret)

        if size_transfered.value != size_to_transfer.value:
            raise spi.SpiError("Error: transfer=%d != transferred=%d",
                               size_to_transfer.value,
                               size_transfered.value)

        return [ord(buffer[i]) for i in range(size_bytes)]

    def readWrite(self, write_buffer, size_bytes=None, options=SPI_TRANSFER_OPTIONS_DEFAULT):

        if size_bytes == None:
            size_bytes = len(write_buffer)

        out_buffer = ctypes.create_string_buffer(size_bytes)
        in_buffer = ctypes.create_string_buffer(size_bytes)

        for i in range(size_bytes):
            out_buffer[i] = write_buffer[i]

        size_to_transfer = ctypes.c_uint32()
        size_to_transfer.value = size_bytes

        size_transfered = ctypes.c_uint32()

        ret = self.dll.SPI_ReadWrite(
            self.handle,
            in_buffer,
            out_buffer,
            size_to_transfer,
            ctypes.byref(size_transfered),
            options
        )

        if ret:
            raise spi.SpiError("Error: read write failed ret=%d" % ret)

        if size_transfered.value != size_to_transfer.value:
            raise spi.SpiError("Error: transfer=%d != transferred=%d",
                               size_to_transfer.value,
                               size_transfered.value)

        return [ord(in_buffer[i]) for i in range(size_bytes)]

    def gpioinit(self):
        ret = self.dll.FT_WriteGPIO(self.handle, self.gpiodir, self.gpioval)
        # if ret:
        #     raise spi.SpiError("Error:FT_WriteGPIO ret=%d" % ret)

    def gpioSetDirOutput(self, gpioPin):
        self.gpiodir = self.gpiodir | gpioPin
        ret = self.dll.FT_WriteGPIO(self.handle, self.gpiodir, self.gpioval)
        # if ret:
        #     raise spi.SpiError("Error:FT_WriteGPIO ret=%d" % ret)

    def gpioSetDirInput(self, gpioPin):
        self.gpiodir = self.gpiodir & (~gpioPin)
        ret = self.dll.FT_WriteGPIO(self.handle, self.gpiodir, self.gpioval)
        if ret:
            raise spi.SpiError("Error:FT_WriteGPIO ret=%d" % ret)

    def gpioSetValue(self, gpioPin):
        self.gpioval = (self.gpioval & (~gpioPin)) | gpioPin
        ret = self.dll.FT_WriteGPIO(self.handle, self.gpiodir, self.gpioval)
        if ret:
            raise spi.SpiError(
                "Error:FT_WriteGPIO ret=%d" % ret)

    def gpioReSetValue(self, gpioPin):
        self.gpioval = (self.gpioval & (~gpioPin))
        ret = self.dll.FT_WriteGPIO(self.handle, self.gpiodir, self.gpioval)
        if ret:
            raise spi.SpiError(
                "Error:FT_WriteGPIO ret=%d" % ret)

    def gpioGetValue(self):
        readValue = ctypes.c_ubyte()
        ret = self.dll.FT_ReadGPIO(self.handle, ctypes.byref(readValue))
        if ret:
            raise spi.SpiError(
                "Error:FT_WriteGPIO ret=%d" % ret)
        # print("read value = %x" % readValue.value)

        return readValue.value



if __name__ == '__main__':
    spidev = spi()
    write = [0xBB, 0xAA, 0x55, 0xCC, 0xDD]

    spidev.write_read(write,len(write))
    spidev.set_pin_rst(True)
    spidev.set_pin_mode(True)
    spidev.deinit()

