from EVtest import EVtest
from instrument.KeysightOSC import OscilloscopeController
from register.test_reg import *


class EVtest_XCLK_Freq(EVtest):
    def __init__(self):
        EVtest.__init__(self)
        self.chip_id = 60
        self.voltcorner = 'NN'
        self.temp = 'RT'
        self.freq = 24
        self.image_path_osc = "C:/Users/Public/Documents/Infiniium/Screen Images/ATC001/OSC/24MHz_Q24FA20H00092"
        self.setup_path_osc = "C:/Users/Public/Documents/Infiniium/setups/ATC001/OSC/"
        self.report_header = ['time', 'chip_id', 'VoltCorner', 'temp', 'p20v33_ds', 'osc_ds', 'freq(MHz)',
                              'C2C_jitter(ps)', 'Period_jitter(ps)', 'RJ(ps)']

    def run(self):
        osc_controller = OscilloscopeController(self.ip_osc)
        osc_controller.connect()
        osc_controller.query_command('*IDN?')
        osc_controller.load_setup(self.setup_path_osc + f'24MHz_frq+periodjitter+C2Cjitter+RJ.set')
        time.sleep(10)
        for osc_ds in [0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7]: #[0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7]
            for p20v33_ds in [0x0, 0x1]:
                print(f'osc_ds = {osc_ds:#x}, p20v33_ds = {p20v33_ds:#x}')
                test_case24_OSC_output_clock(osc_ds, p20v33_ds)
                osc_controller.send_command(f':ANALyze:CLOCk:METHod:OJTF SOPLL,{self.freq*2}E+06,30.00E+03,707E-03')
                osc_controller.send_command(':CDISplay')
                osc_controller.send_command(':RUN')
                time.sleep(15)
                osc_controller.send_command(':STOP')
                time.sleep(5)
                osc_controller.send_command(':MEASure:STATistics STDDev')
                MeasResults = osc_controller.query_command(' :MEASure:RESults?')
                C2C_jitter = round(float(MeasResults.split(',')[2].replace('\n', '')) * 1e12, 2)
                Period_jitter = round(float(MeasResults.split(',')[1]) * 1e12, 2)
                osc_controller.send_command(':MEASure:STATistics MEAN')
                MeasResults = osc_controller.query_command(' :MEASure:RESults?')
                freq = round(float(MeasResults.split(',')[0]) / 1e6, 5)
                RJDJALL = osc_controller.query_command(':MEASure:RJDJ:ALL?')
                RJ = round(float(RJDJALL.split(',')[4]) * 1e12, 2)
                print(f'C2C_jitter = {C2C_jitter}, Period_jitter = {Period_jitter}, RJ = {RJ}')
                current_time = datetime.now()
                formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
                result = [formatted_time, self.chip_id, self.voltcorner, self.temp, hex(p20v33_ds), hex(osc_ds),
                          freq, C2C_jitter, Period_jitter, RJ]
                self.write_to_csv([result], './report/ATC001_OSC_output.csv', self.report_header)
                osc_controller.save_image(
                    self.image_path_osc + f'test_ATC001_{self.chip_id}#@A03_OSC_{self.freq}MHz_OSCDS{osc_ds}_P20DS{p20v33_ds}_Jitter_{self.temp}+{self.voltcorner}')
                # input("Press Enter to continue...")
        osc_controller.disconnect()


if __name__ == "__main__":
    test = EVtest_XCLK_Freq()
    test.run()
