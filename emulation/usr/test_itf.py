from fractions import Fraction
import os
import sys
import time
import random
from collections import Counter
file_dir = os.path.dirname(__file__)
spi_dir = file_dir + '\\..' + '\\drivers'
sys.path.append(spi_dir)
from spi import spi
from common.utils.log import log

# from test_cmd import test_cmd
# from reram import reram

class test_itf:
    PRINT_ENABLE = False # register config process print

    def __init__(self, dev_spi: spi):
        self.dev_spi = dev_spi
        self.dev_spi.set_pin_rst(True)
        self.dev_spi.set_pin_stRst(True)
        self.dev_spi.set_pin_adcRegTrg(False)
        self.dev_spi.set_pin_adcInjTrg(False)
        self.test_command_table = {
            'reset'     : self.reset,
            'read'      : self.read_reg,
            'write'     : self.write_reg,
            'sel'       : self.adc_sel,
            'init'      : self.adc_init,
            'regular'   : self.adc_regular,
            'inject'    : self.adc_inject,
            'start'     : self.adc_start,
            'data'      : self.adc_data,
            'awd'       : self.adc_awd,
            'dma'       : self.adc_dma,
            'cali'      : self.adc_cali,
            'hwtrg'     : self.adc_hwtrigger,
            'iodir'     : self.gpio_dir,
            'iodata'    : self.gpio_data,
            'aclk'      : self.adc_aclkdiv4,
            'parallel'  : self.adc_parallel,
            'sync'      : self.adc_sync,
            'dual'      : self.adc_dual,
            'hsetest'   : self.hsetest,
            'Biasref'   : self.Biasref,
        }
        self.CLKCON = 0x50000000
        self.ANACON0 = 0x50000008
        self.ANACON1 = 0x5000000C
        self.PADDATA = 0x5000001C
        self.PADDIR = 0x50000020

    def reset(self, args: list):
        self.dev_spi.set_pin_rst(False)  # pin3
        self.dev_spi.set_pin_stRst(False)  # pin5
        time.sleep(0.01)
        self.dev_spi.set_pin_rst(True)
        self.dev_spi.set_pin_stRst(True)  # pin5
        print('reset device')

    def readReg(self, regaddress):
        buf = [0 for _ in range(11)]
        buf[0] = 0x55
        buf[1] = 0xaa
        buf[2] = 0x22 # read cmd
        buf[3] = regaddress >> 24 & 0xFF
        buf[4] = regaddress >> 16 & 0xFF
        buf[5] = regaddress >> 8 & 0xFF
        buf[6] = regaddress >> 0 & 0xFF
        buf[7] = 0x00
        buf[8] = 0x00
        buf[9] = 0x00
        buf[10] = 0x00
        self.dev_spi.write_read(buf, len(buf))
        data = 0
        data = buf[7] << 24 | buf[8] << 16 | buf[9] << 8 | buf[10]
        if test_itf.PRINT_ENABLE == True:
            print(f'reg = {hex(regaddress)}, data = {hex(data)}')
        return data
        # if buf[2] != 0xFF:
        #     print(f'Read Reg {hex(regaddress)} Fail, VerifyValue = {buf[2]} ReadValue = {(buf[3] << 24 | buf[4] << 16 | buf[5] << 8 | buf[6])}')
        # return (buf[3] << 24 | buf[4] << 16 | buf[5] << 8 | buf[6])

    def readReg_print(self, regaddress):
        buf = [0 for _ in range(11)]
        buf[0] = 0x55
        buf[1] = 0xaa
        buf[2] = 0x22 # read cmd
        buf[3] = regaddress >> 24 & 0xFF
        buf[4] = regaddress >> 16 & 0xFF
        buf[5] = regaddress >> 8 & 0xFF
        buf[6] = regaddress >> 0 & 0xFF
        buf[7] = 0x00
        buf[8] = 0x00
        buf[9] = 0x00
        buf[10] = 0x00
        self.dev_spi.write_read(buf, len(buf))
        data = 0
        data = buf[7] << 24 | buf[8] << 16 | buf[9] << 8 | buf[10]
        print(f'reg = {hex(regaddress)}, data = {hex(data)}')
        log.info(f'reg = {hex(regaddress)}, data = {hex(data)}')

    def WriteReg(self, regaddress, value):
        buf = [0 for _ in range(11)]
        buf[0] = 0x55
        buf[1] = 0xaa
        buf[2] = 0x11 # write cmd
        buf[3] = regaddress >> 24 & 0xFF
        buf[4] = regaddress >> 16 & 0xFF
        buf[5] = regaddress >> 8 & 0xFF
        buf[6] = regaddress >> 0 & 0xFF
        buf[7] = value >> 24 & 0xFF
        buf[8] = value >> 16 & 0xFF
        buf[9] = value >> 8 & 0xFF
        buf[10] = value >> 0 & 0xFF
        self.dev_spi.write_read(buf, len(buf))
        # if buf[6] != 0xFF:
        #     print(f'Write Reg {hex(regaddress)} Fail, VerifyValue = {buf[6]}')

        # return buf[6]

    def write_reg_bits(self, reg_addr: int, reg_mask: int, set_mask: int):
        '''
        Write some bits in the regsiter.
        :param reg_addr: The address of register, uint32
        :param reg_mask: Mask for bits to set or clear, uint32
        :param set_mask: Value of bits, uint32
        :return:
        '''
        reg_val = self.readReg(reg_addr)
        reg_val &= (~reg_mask)
        reg_val |= set_mask
        self.WriteReg(reg_addr, reg_val)

    def read_reg(self, args: list):
        return self.readReg_print(args[0])

    def write_reg(self, args: list):
        self.WriteReg(args[0], args[1])

    def adc_sel(self, args: list):
        # definition address of registers
        self.BASE_ADDR = 0x40020000 if args[0] == 1 else 0x40040000 # ADC1:0x40020000 ADC2:0x40040000
        self.ISR = self.BASE_ADDR + 0x00
        self.IER = self.BASE_ADDR + 0x04
        self.CR = self.BASE_ADDR + 0x08
        self.CFGR = self.BASE_ADDR + 0x0C
        self.CFGR2 = self.BASE_ADDR + 0x10
        self.CFGR3 = self.BASE_ADDR + 0x14
        self.SMPR1 = self.BASE_ADDR + 0x18
        self.ADW1CR = self.BASE_ADDR + 0x38
        self.LTR1 = self.BASE_ADDR + 0x44
        self.HTR1 = self.BASE_ADDR + 0x48
        self.SQR1 = self.BASE_ADDR + 0x60
        self.SQR2 = self.BASE_ADDR + 0x64
        self.SQR3 = self.BASE_ADDR + 0x68
        self.SQR4 = self.BASE_ADDR + 0x6C
        self.DR = self.BASE_ADDR + 0x70
        self.JSQR = self.BASE_ADDR + 0x74
        self.DRSQ1 = self.BASE_ADDR + 0x80
        self.DRSQ2 = self.BASE_ADDR + 0x84
        self.DRSQ3 = self.BASE_ADDR + 0x88
        self.DRSQ4 = self.BASE_ADDR + 0x8C
        self.DRSQ5 = self.BASE_ADDR + 0x90
        self.DRSQ6 = self.BASE_ADDR + 0x94
        self.DRSQ7 = self.BASE_ADDR + 0x98
        self.DRSQ8 = self.BASE_ADDR + 0x9C
        self.DRSQ9 = self.BASE_ADDR + 0xA0
        self.DRSQ10 = self.BASE_ADDR + 0xA4
        self.DRSQ11 = self.BASE_ADDR + 0xA8
        self.DRSQ12 = self.BASE_ADDR + 0xAC
        self.DRSQ13 = self.BASE_ADDR + 0xB0
        self.DRSQ14 = self.BASE_ADDR + 0xB4
        self.DRSQ15 = self.BASE_ADDR + 0xB8
        self.DRSQ16 = self.BASE_ADDR + 0xBC
        self.JDR1 = self.BASE_ADDR + 0xC0
        self.JDR2 = self.BASE_ADDR + 0xC4
        self.JDR3 = self.BASE_ADDR + 0xC8
        self.JDR4 = self.BASE_ADDR + 0xCC
        self.CALOFACT = self.BASE_ADDR + 0xD0
        self.CALUSER1 = self.BASE_ADDR + 0xD4
        self.CALUSER2 = self.BASE_ADDR + 0xD8
        self.CALUSER3 = self.BASE_ADDR + 0xDC
        self.DIFSEL = self.BASE_ADDR + 0xE0
        self.CALFACT1 = self.BASE_ADDR + 0xE4
        self.CALFACT2 = self.BASE_ADDR + 0xE8

        # print(hex(self.BASE_ADDR))
        # print(hex(self.CFGR))

        # if args[0] in self.ddicreg:
        #     self.WriteReg(self.ddicreg[args[0]], value)
    def adc_msp_init(self):
        self.write_reg_bits(0x50011838, (0x7 << 27),    0x0 << 27)  # Enable clock
        self.write_reg_bits(0x50011854, (0x7 << 20),    0x0 << 20)  # Enable analg clock
        self.write_reg_bits(0x50011C40, (0x3 << 6),     0x3 << 6)   # Analog PC03
        self.write_reg_bits(0x50011C40, (0x3 << 4),     0x3 << 4)   # Analog PC02

    def adc_init(self, args: list):
        self.adc_msp_init()
        self.write_reg_bits(0x50011418, (0x1 << 2),     0x1 << 2) # BGEN
        self.write_reg_bits(self.CLKCON,(0x3 << 30),    0x3 << 30) # AD soft reset disable
        self.write_reg_bits(self.CR,    (0xF << 12),    args[0] << 12)  # CKDIV
        self.write_reg_bits(self.CR,    (0x7 << 9),     args[1] << 9)  # RES
        self.write_reg_bits(self.CFGR,  (0x1 << 8),     args[2] << 8)  # CONT
        self.write_reg_bits(self.SQR1,  (0xF << 0),     args[3] << 0)  # Length
        if args[4] > 0:
            self.write_reg_bits(self.CFGR,  (0x7 << 10),    (args[4] - 1) << 10)  # DISCUM
            self.write_reg_bits(self.CFGR,  (0x1 << 9),     1 << 9)  # DISCEN
        self.write_reg_bits(self.CFGR,  (0x3 << 5),     args[5] << 5)  # EXTEN
        self.write_reg_bits(self.CFGR2, (0x3 << 0),     args[6] << 0)  # Oversampling scope
        self.write_reg_bits(self.CFGR2, (0x3FF << 16),  args[7] << 16)  # Oversampling ratio
        self.write_reg_bits(self.CFGR2, (0xF << 4),     args[8] << 4)  # Oversampling shift
        self.write_reg_bits(self.CR,    (0x1 << 6),     0x1 << 6) # VCMEN
        print('Initial ADC')

    def adc_regular(self, args: list):
        ch = args[0]
        self.write_reg_bits(self.SQR1,  (0x1F << 6),    ch << 6)  # Rank
        self.write_reg_bits(self.SMPR1, (0x3FF << 0),   args[1] << 0)  # sample time
        self.write_reg_bits(self.DIFSEL,(1 << ch),      args[2] << ch)  # diff mode
        print('ADC regular group config')

    def adc_inject(self, args: list):
        ch = args[0]
        self.write_reg_bits(self.JSQR,  (0x1F << 9),    ch << 9)  # Rank
        self.write_reg_bits(self.SMPR1, (0x3FF << 0),   args[1] << 0)  # sample time
        self.write_reg_bits(self.DIFSEL,(1 << ch),      args[2] << ch)  # diff mode
        self.write_reg_bits(self.JSQR,  (0x3 << 0),     args[3] << 0) # Length
        self.write_reg_bits(self.JSQR,  (0x3 << 7),     args[4] << 7) # JEXTEN
        self.write_reg_bits(self.JSQR,  (0x1F << 9),    args[5] << 9) # Rank
        self.write_reg_bits(self.CFGR,  (0x1 << 13),    args[6] << 13) # JDISCEN
        self.write_reg_bits(self.CFGR,  (0x1 << 14),    args[7] << 14) # JAUTO
        print('ADC injected group config')

    def adc_start(self, args: list):
        self.write_reg_bits(self.CR,  (0x1 << 0),   0x1 << 0)  # ADEN
        time.sleep(0.01)

        if args[0] == 0: # regular
            if args[1] == 1:
                self.write_reg_bits(self.CR,  (0x1 << 2),   0x1 << 2)  # ADSTART
            else:
                self.write_reg_bits(self.CR,  (0x1 << 4),   0x1 << 4)  # ADSTP
        elif args[0] == 1: # inject
            if args[1] == 1:
                self.write_reg_bits(self.CR,  (0x1 << 3),   0x1 << 3)  # JADSTART
            else:
                self.write_reg_bits(self.CR,  (0x1 << 5),   0x1 << 5)  # JADSTP
        elif args[0] == 2:
            # start_time = time.time()
            self.write_reg_bits(self.CR,  (0x1 << 2),   0x1 << 2)  # ADSTART
            # end_time = time.time()
            # print(f'excution time:{end_time-start_time}')
            self.write_reg_bits(self.CR,  (0x1 << 2),   0x1 << 2)  # ADSTART
        elif args[0] == 3:
            self.write_reg_bits(self.CR,  (0x1 << 2),   0x1 << 2)  # ADSTART
            self.write_reg_bits(self.CR,  (0x1 << 3),   0x1 << 3)  # JADSTART
        elif args[0] == 4:
            self.write_reg_bits(self.CR,  (0x1 << 3),   0x1 << 3)  # JADSTART
            self.write_reg_bits(self.CR,  (0x1 << 3),   0x1 << 3)  # JADSTART
        elif args[0] == 5:
            self.write_reg_bits(self.CR,  (0x1 << 3),   0x1 << 3)  # JADSTART
            self.write_reg_bits(self.CR,  (0x1 << 2),   0x1 << 2)  # ADSTART
        elif args[0] == 6:
            self.write_reg_bits(self.CR,  (0x3 << 2),   0x3 << 2)  # ADSTART & JADSTART
        print('ADC start')

    def adc_data(self, args: list):
        print('adc data----------------------------------------')
        self.readReg_print(self.ISR),
        self.readReg_print(self.DR),
        # self.readReg_print(self.DRSQ1),
        # self.readReg_print(self.DRSQ2),
        # self.readReg_print(self.DRSQ3),
        # self.readReg_print(self.DRSQ4),
        # self.readReg_print(self.DRSQ5),
        # self.readReg_print(self.DRSQ6),
        # self.readReg_print(self.DRSQ7),
        # self.readReg_print(self.DRSQ8),
        # self.readReg_print(self.DRSQ9),
        # self.readReg_print(self.DRSQ10),
        # self.readReg_print(self.DRSQ11),
        # self.readReg_print(self.DRSQ12),
        # self.readReg_print(self.DRSQ13),
        # self.readReg_print(self.DRSQ14),
        # self.readReg_print(self.DRSQ15),
        # self.readReg_print(self.DRSQ16),
        # self.readReg_print(self.JSQR)
        self.readReg_print(self.JDR1),
        self.readReg_print(self.JDR2),
        self.readReg_print(self.JDR3),
        self.readReg_print(self.JDR4),
        # print('adc config----------------------------------------')
        # self.readReg_print(self.IER),
        # self.readReg_print(self.CR),
        # self.readReg_print(self.CFGR),
        # self.readReg_print(self.CFGR2),
        # self.readReg_print(self.CFGR3),
        # self.readReg_print(self.SMPR1),
        # self.readReg_print(self.ADW1CR),
        # self.readReg_print(self.LTR1),
        # self.readReg_print(self.HTR1),
        # self.readReg_print(self.SQR1),
        # self.readReg_print(self.SQR2),
        # self.readReg_print(self.SQR3),
        # self.readReg_print(self.SQR4),
        # self.readReg_print(self.JSQR),
        # self.readReg_print(self.CALOFACT),
        # self.readReg_print(self.CALUSER1),
        # self.readReg_print(self.CALUSER2),
        # self.readReg_print(self.CALUSER3),
        # self.readReg_print(self.DIFSEL),
        # self.readReg_print(self.CALFACT1),
        # self.readReg_print(self.CALFACT2),



    def adc_awd(self, args: list):
        num = args[0]
        self.write_reg_bits(self.ADW1CR + (num * 4),  (0x1 << args[1]),   0x1 << args[1])
        self.write_reg_bits(self.HTR1 + (num * 8),  0x3FFFFFF,    args[2])
        self.write_reg_bits(self.LTR1 + (num * 8),  0x3FFFFFF,    args[3])

    def adc_dma(self, args: list):
        if (args[0] == 1):### ADC1 DMA1_CH0
            print('Inital ADC1 DMA')
            self.WriteReg(0x40000044, (0 << 7) |0x4) # DMA1_CH0->CFGH
            self.WriteReg(0x40000040, 0x1 << 30) # DMA1_CH0->CFGL SRC_RELOAD=1
            self.WriteReg(0x4000001C, 0x0) # DMA1_CH0->CTLH
            self.WriteReg(0x40000018, 0x200424) # DMA1_CH0->CTLL addr&size
            # self.WriteReg(0x5001004C, 0x08000000) #SYSCFG->CORE1INTEN0
            self.write_reg_bits(self.CR,  (0x1 << 0),   0x1 << 0)  # ADEN
            self.write_reg_bits(self.CFGR,  (0x1 << 0),   0x1 << 0)  # DMAEN
            self.WriteReg(0x40000000, 0x40020070) # Src addr ADC1 DR
            self.WriteReg(0x40000008, 0x30000000) # Dst addr
            self.WriteReg(0x40000330, 0x1) # DMA mask err
            self.WriteReg(0x40000310, 0x1) # DMA mask tfr
            self.WriteReg(0x40000318, 0x1) # DMA mask blk
            self.WriteReg(0x4000001C, 0xFFF) # DMA block ts   2048byte/4=512 block, need < 4095
            self.WriteReg(0x40000018, 0xA00424) # DMA DMS=1
            # self.WriteReg(0x40000018, 0xA00425) # DMA INTEN=1
            self.WriteReg(0x40000398, 0x1) # DMA Enable
            self.WriteReg(0x400003A0, (0x1 << 8 | 0x1)) # DMA CH Write Enable & CH Enable
        else:### ADC2 DMA1_CH1
            print('Inital ADC2 DMA')
            self.WriteReg(0x4000009C, (1 << 7) | 0x4) # DMA1_CH1->CFGH
            self.WriteReg(0x40000098, 0x1 << 30) # DMA1_CH1->CFGL SRC_RELOAD=1
            self.WriteReg(0x40000074, 0x0) # DMA1_CH1->CTLH
            self.WriteReg(0x40000070, 0x200424) # DMA1_CH1->CTLL addr&size
            # self.WriteReg(0x5001004C, 0x08000000) #SYSCFG->CORE1INTEN0
            self.write_reg_bits(self.CR,  (0x1 << 0),   0x1 << 0)  # ADEN
            self.write_reg_bits(self.CFGR,  (0x1 << 0),   0x1 << 0)  # DMAEN
            self.WriteReg(0x40000058, 0x40040070) # Src addr ADC2 DR
            self.WriteReg(0x40000060, 0x30000000) # Dst addr
            self.WriteReg(0x40000330, 0x1) # DMA mask err
            self.WriteReg(0x40000310, 0x1) # DMA mask tfr
            self.WriteReg(0x40000318, 0x1) # DMA mask blk
            self.WriteReg(0x40000074, 0xFFF) # DMA block ts   2048byte/4=512 block, need < 4095
            self.WriteReg(0x40000070, 0xA00424) # DMA DMS=1
            # self.WriteReg(0x40000070, 0xA00425) # DMA INTEN=1
            self.WriteReg(0x40000398, 0x1) # DMA Enable
            self.WriteReg(0x400003A0, (0x2 << 8 | 0x2)) # DMA CH Write Enable & CH Enable

        self.write_reg_bits(self.CR,  (0x1 << 2),   0x1 << 2)  # ADSTART

        # self.readReg_print(self.CR)
        # self.readReg_print(self.CFGR)
        # self.readReg_print(self.CFGR2)

        # DMA1_CH0
        # self.readReg_print(0x40000058)
        # self.readReg_print(0x40000060)
        # self.readReg_print(0x40000074)
        # self.readReg_print(0x40000070)
        # self.readReg_print(0x4000009C)
        # DMA1_CH1
        # self.readReg_print(0x40000000)
        # self.readReg_print(0x40000008)
        # self.readReg_print(0x40000018)
        # self.readReg_print(0x4000001C)

        # self.readReg_print(0x40000398)
        # self.readReg_print(0x400003A0)
        # for i in range(0, 4095):
        #     self.WriteReg(0x30000000 + (4*i), i)

        for i in range(0, 8192): # 4095
            self.readReg_print(0x30000000 + (4*i)) #SRAM0 addr

    def adc_cali(self, args: list):
        self.write_reg_bits(self.CFGR2,     (0x1 << 27),    args[0] << 27)  # OFACTEN  EnableCalibrationFactor
        self.write_reg_bits(self.CALOFACT,  (0xFFFF << 0),  args[1] << 0)  # SOFACT
        self.write_reg_bits(self.CALOFACT,  (0xFFFF << 16), args[2] << 16)  # DOFACT

    def adc_hwtrigger(self, args: list):
        self.write_reg_bits(self.ANACON0,   (0x1 << 22),    args[0] << 22) # adc1 reguar trigger
        self.write_reg_bits(self.ANACON0,   (0x1 << 23),    args[1] << 23) # adc2 reguar trigger
        self.write_reg_bits(self.ANACON0,   (0x1 << 20),    args[2] << 20) # adc1 injected trigger
        self.write_reg_bits(self.ANACON0,   (0x1 << 21),    args[3] << 21) # adc2 injected trigger
        # self.readReg_print(self.ANACON0)
        time.sleep(0.001)
        self.dev_spi.set_pin_adcRegTrg(True)
        self.dev_spi.set_pin_adcInjTrg(True)
        time.sleep(0.01)
        self.dev_spi.set_pin_adcRegTrg(False)
        self.dev_spi.set_pin_adcInjTrg(False)

    def gpio_dir(self, args: list):
        self.write_reg_bits(self.PADDIR,    (0x1 << args[0]),  args[1] << args[0])
        self.readReg_print(self.PADDIR)

    def gpio_data(self, args: list):
        if args[0] == '0':
            self.readReg_print(self.PADDATA)
            self.readReg_print(self.ANACON0)
        else:
            self.write_reg_bits(self.PADDATA,   (0x1 << args[0]),  args[1] << args[0])

    def adc_aclkdiv4(self, args: list):
        self.write_reg_bits(self.ANACON0,    (0x1 << 16),  args[0] << 16) # P19V33
        self.write_reg_bits(self.ANACON0,    (0x1 << 17),  args[1] << 17) # P20V33

    def adc_parallel(self, args: list):
        self.write_reg_bits(self.ANACON0,   (0x3 << 24),  args[0] << 24) # ADC Digital
        self.write_reg_bits(self.ANACON0,   (0x3 << 26),  args[1] << 26) # ADC Analog
        self.write_reg_bits(self.ANACON0,   (0x3 << 28),  args[2] << 28) # ADC1 EOC width
        self.write_reg_bits(self.ANACON0,   (0x3 << 30),  args[3] << 30) # ADC2 EOC width

    def adc_sync(self, args: list):
        self.write_reg_bits(self.ANACON1,    (0x1 << 5),  args[0] << 5)
        self.write_reg_bits(self.ANACON1,    (0xF << 0),  args[1] << 0)
        self.write_reg_bits(self.ANACON1,    (0x1 << 4),  args[2] << 4)
        self.readReg_print(self.ANACON1)

    def adc_dual(self, args: list):
        self.write_reg_bits(self.CFGR3,     0xFFFF,         args[0])
        self.write_reg_bits(self.CFGR,     (0x3 << 16),    args[1] << 16)

    def hsetest(self, args: list):
        # args[0] = probe_clk0_div
        # args[1] = p19v33_ds
        self.write_reg_bits(0x50000000,    (0x1 << 0),  0x0 << 0) # sys_clk_sel=0 from xclk
        self.write_reg_bits(0x50000000,    (0x1 << 12),  0x0 << 12) # sys_div=0x00 disable
        self.write_reg_bits(0x50000000,    (0x1F << 3),  args[0] << 3) # HSE enable  probe_clk0_div=0x13  0x50000000  self.CLKCON
        self.write_reg_bits(0x50000000,    (0x1 << 25),  0x0 << 25) # probe_clk0_sel=0 from hclk
        print('hclk has been set to hse')
        self.write_reg_bits(0x50000008,    (0x1 << 16),  0x0 << 16) # adc1_aclk_d4_sel=0
        self.write_reg_bits(0x50000008,    (0x1 << 18),  0x1 << 18) # probe_clk0=1
        self.write_reg_bits(0x50000028,    (0x1 << 23),  args[1] << 23) # PAD_DS[23] p19v33_ds=0
        print('hclk port')
        self.readReg_print(0x50000000)
        self.readReg_print(0x50000008)
        self.readReg_print(0x50000028)
        time.sleep(3)

    def Biasref(self, args: list):
        print('begin to set Biasref')
        self.write_reg_bits(0x5000000C, (0xF << 12), 0x0 << 12)  # ANA_CON1 bit 15:12
        self.write_reg_bits(0x400200F8, (0x1 << 24), 0x0 << 24)  # ADC1_MUX_FT disable ADC1_CFGR_FT bit 24
        self.write_reg_bits(0x400400F8, (0x1 << 24), 0x0 << 24)  # ADC2_MUX_FT disable ADC1_CFGR_FT bit 24
        self.write_reg_bits(0x5000000C, (0x1 << 17), 0x1 << 17)  # Set itest switch connect. ANA_CON1 bit 17
        self.write_reg_bits(0x5000000C, (0x1 << 16), 0x1 << 16)  # Enable Bias IREF. ANA_CON1 bit 16
        time.sleep(1)
        for i in range(16):
            print(f"Please Press key to continue: {i}")
            self.write_reg_bits(0x5000000C, (0xF << 12), i << 12)  # ANA_CON1 bit 15:12
            input()

        print('test end')

if __name__ == '__main__':
    pass