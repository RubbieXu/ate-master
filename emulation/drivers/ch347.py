import ctypes
import os
import sys
# Load the CH347DLL library
# ch347dll = ctypes.WinDLL("./CH347DLL.DLL")  # Update the filename if necessary
# ch347dll = ctypes.cdll.LoadLibrary("./CH347DLL.LIB")  # Update the filename if necessary
# work_dir = os.getcwd() + '\emulation' + '\lib' + '\CH347DLLA64.DLL'
#work_dir = os.getcwd() + '\emulation' + '\lib' + '\CH347DLL.DLL'
file_dir = os.path.dirname(__file__)
work_dir = file_dir + '\..' + '\lib'
if sys.maxsize > 2 ** 32:   # for 64-bit python version.
    ch347_64_dll = work_dir + '.\CH347DLLA64.DLL'
    ch347dll = ctypes.WinDLL(ch347_64_dll)  # if python is 64 bits, use this library
else:   # for 32-bit python version.
    ch347_32_dll = work_dir + '\CH347DLL.DLL'
    ch347dll = ctypes.WinDLL(ch347_32_dll)  # if python is 32 bits, use this library

# Define the argument and return types for CH347OpenDevice
ch347dll.CH347OpenDevice.argtypes = [ctypes.c_ulong]
ch347dll.CH347OpenDevice.restype = ctypes.c_bool

# Define the argument and return types for CH347CloseDevice
ch347dll.CH347CloseDevice.argtypes = [ctypes.c_ulong]
ch347dll.CH347CloseDevice.restype = ctypes.c_bool

# Define the argument and return types for CH347GetDeviceInfor
MAX_PATH = 260

class mDeviceInforS(ctypes.Structure):
    _fields_ = [("iIndex", ctypes.c_ubyte),
                ("DevicePath", ctypes.c_char * MAX_PATH),
                ("UsbClass", ctypes.c_ubyte),
                ("FuncType", ctypes.c_ubyte),
                ("DeviceID", ctypes.c_char * 64),
                ("ChipMode", ctypes.c_ubyte),
                ("DevHandle", ctypes.c_void_p),
                ("BulkOutEndpMaxSize", ctypes.c_ushort),
                ("BulkInEndpMaxSize", ctypes.c_ushort),
                ("UsbSpeedType", ctypes.c_ubyte),
                ("CH347IfNum", ctypes.c_ubyte),
                ("DataUpEndp", ctypes.c_ubyte),
                ("DataDnEndp", ctypes.c_ubyte),
                ("ProductString", ctypes.c_char * 64),
                ("ManufacturerString", ctypes.c_char * 64),
                ("WriteTimeout", ctypes.c_ulong),
                ("ReadTimeout", ctypes.c_ulong),
                ("FuncDescStr", ctypes.c_char * 64),
                ("FirewareVer", ctypes.c_ubyte)]

ch347dll.CH347GetDeviceInfor.argtypes = [ctypes.c_ulong, ctypes.POINTER(mDeviceInforS)]
ch347dll.CH347GetDeviceInfor.restype = ctypes.c_bool

# Define the argument and return types for CH347GetVersion
ch347dll.CH347GetVersion.argtypes = [
    ctypes.c_ulong,
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.POINTER(ctypes.c_ubyte)
]
ch347dll.CH347GetVersion.restype = ctypes.c_bool

# Define the argument and return types for CH347SPI_Init
class mSpiCfgS(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ("iMode", ctypes.c_ubyte),
            ("iClock", ctypes.c_ubyte),
            ("iByteOrder", ctypes.c_ubyte),
            ("iSpiWriteReadInterval", ctypes.c_ushort),
            ("iSpiOutDefaultData", ctypes.c_ubyte),
            ("iChipSelect", ctypes.c_ulong),
            ("CS1Polarity", ctypes.c_ubyte),  
            ("CS2Polarity", ctypes.c_ubyte), 
            ("iIsAutoDeativeCS", ctypes.c_ushort), 
            ("iActiveDelay", ctypes.c_ushort), 
            ("iDelayDeactive", ctypes.c_ulong),]

ch347dll.CH347SPI_Init.argtypes = [ctypes.c_ulong, ctypes.POINTER(mSpiCfgS)]
ch347dll.CH347SPI_Init.restype = ctypes.c_bool

# Define the argument and return types for CH347SPI_GetCfg
ch347dll.CH347SPI_GetCfg.argtypes = [ctypes.c_ulong, ctypes.POINTER(mSpiCfgS)]
ch347dll.CH347SPI_GetCfg.restype = ctypes.c_bool

# Define the argument and return types for CH347SPI_Write
ch347dll.CH347SPI_Write.argtypes = [ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong)]
ch347dll.CH347SPI_Write.restype = ctypes.c_bool

# Define the argument and return types for CH347SPI_Read
ch347dll.CH347SPI_Read.argtypes = [ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_ulong)]
ch347dll.CH347SPI_Read.restype = ctypes.c_bool

# Define the argument and return types for CH347SPI_WriteRead
class spi_buffer(ctypes.Structure):
        _fields_ = [
            ("filed", ctypes.c_ubyte*(32768 + 4)),
        ]

ch347dll.CH347SPI_WriteRead.argtypes = [ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(spi_buffer)]
ch347dll.CH347SPI_WriteRead.restype = ctypes.c_bool

ch347dll.CH347StreamSPI4.argtypes = [ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(spi_buffer)]
ch347dll.CH347StreamSPI4.restype = ctypes.c_bool


# Define the argument and return types for CH347GPIO_Get
ch347dll.CH347GPIO_Get.argtypes = [ctypes.c_ulong, ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte)]
ch347dll.CH347GPIO_Get.restype = ctypes.c_bool

def OpenDevice(DevI):
    # Call the CH347OpenDevice function
    return ch347dll.CH347OpenDevice(DevI)


def SetTimeout(DevI, iWriteTimeout, iReadTimeout):
    # Call the CH347OpenDevice function
    return ch347dll.CH347SetTimeout(DevI, iWriteTimeout, iReadTimeout)

def CloseDevice(iIndex):
    # Call the CH347CloseDevice function
    return ch347dll.CH347CloseDevice(iIndex)

def GetDeviceInfor(iIndex):
    # Create an instance of mDeviceInforS structure
    dev_info = mDeviceInforS()

    # Call the CH347GetDeviceInfor function
    result = ch347dll.CH347GetDeviceInfor(iIndex, ctypes.byref(dev_info))

    # Return the result and device information
    return result, dev_info

def GetVersion(iIndex):
    # Create variables to store the version information
    driver_ver = ctypes.c_ubyte()
    dll_ver = ctypes.c_ubyte()
    device_ver = ctypes.c_ubyte()
    chip_type = ctypes.c_ubyte()

    # Call the CH347GetVersion function
    result = ch347dll.CH347GetVersion(iIndex,
                                      ctypes.byref(driver_ver),
                                      ctypes.byref(dll_ver),
                                      ctypes.byref(device_ver),
                                      ctypes.byref(chip_type))

    # Return the result and version information
    return result, driver_ver.value, dll_ver.value, device_ver.value, chip_type.value

def SPI_Init(iIndex, spi_config):
    result = ch347dll.CH347SPI_Init(iIndex, ctypes.byref(spi_config))
    return result

def SPI_Write(iIndex, iChipSelect, iLength, iWriteStep, ioBuffer):
    result = ch347dll.CH347SPI_Write(iIndex, iChipSelect, iLength, iWriteStep, ctypes.byref(ioBuffer))
    return result

def SPI_Read(iIndex, iChipSelect, oLength, iLength, ioBuffer):
    result = ch347dll.CH347SPI_Read(iIndex, iChipSelect, oLength, iLength, ctypes.byref(ioBuffer))
    return result

def SPI_WriteRead(iIndex, iChipSelect, iLength, ioBuffer):
    result = ch347dll.CH347SPI_WriteRead(iIndex, iChipSelect, iLength, ctypes.byref(ioBuffer))
    return result

def SPI_StreamWriteRead(iIndex, iChipSelect, iLength, ioBuffer):
    result = ch347dll.CH347StreamSPI4(iIndex, iChipSelect, iLength, ctypes.byref(ioBuffer))
    return result

def SPI_GetCfg(iIndex):
    spi_config = mSpiCfgS()
    result = ch347dll.CH347SPI_GetCfg(iIndex, ctypes.byref(spi_config))
    return result, spi_config

def GPIO_GetValue(iIndex):
    direction = ctypes.c_ubyte()
    level = ctypes.c_ubyte()
    ch347dll.CH347GPIO_Get(iIndex, ctypes.byref(direction), ctypes.byref(level))
    return direction, level

def GPIO_SetValue(iIndex, iEnable, iSetDirOut, iSetDataOut):
    ch347dll.CH347GPIO_Set(iIndex, iEnable, iSetDirOut, iSetDataOut)
