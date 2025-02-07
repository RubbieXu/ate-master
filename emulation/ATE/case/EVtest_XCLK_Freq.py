from EVtest import EVtest
from instrument.KeysightOSC import OscilloscopeController
from register.test_reg import *


class EVtest_XCLK_Freq(EVtest):
    def __init__(self):
        EVtest.__init__(self)
        self.chip_id = 3
        self.voltcorner = 'NN'
        self.temp = 'RT'
        self.image_path_osc = "C:/Users/Public/Documents/Infiniium/Screen Images/ATC001/XCLK/"
        self.setup_path_osc = "C:/Users/Public/Documents/Infiniium/setups/ATC001/XCLK/"
        self.report_header = ['time', 'chip_id', 'VoltCorner', 'temp', 'probe_clk0_div', 'p19v33_ds', 'freq',
                              'C2C_jitter', 'Period_jitter', 'RJ']

    def run(self):
        osc_controller = OscilloscopeController(self.ip_osc)
        osc_controller.connect()
        osc_controller.query_command('*IDN?')
        osc_controller.load_setup(self.setup_path_osc + f'50M_frq+periodjitter+C2Cjitter+RJ.set')
        time.sleep(10)
        for probe_clk0_div in [0x13, 0x14, 0x17]:
            for p19v33_ds in [0x0, 0x1]:
                print(f'probe_clk0_div = {probe_clk0_div:#x}, p19v33_ds = {p19v33_ds:#x}')
                freq = int(200 / ((probe_clk0_div & 0x0f) + 1))
                test_case23_XCLK_Freq(probe_clk0_div, p19v33_ds)
                osc_controller.send_command(f':ANALyze:CLOCk:METHod:OJTF SOPLL,{freq}E+06,30.00E+03,707E-03')
                osc_controller.send_command(':CDISplay')
                osc_controller.send_command(':RUN')
                time.sleep(15)
                osc_controller.send_command(':STOP')
                time.sleep(5)
                osc_controller.send_command(':MEASure:STATistics STDDev')
                MeasResults = osc_controller.query_command(' :MEASure:RESults?')
                C2C_jitter = round(float(MeasResults.split(',')[2].replace('\n', '')) * 1e12, 2)
                Period_jitter = round(float(MeasResults.split(',')[1]) * 1e12, 2)
                RJDJALL = osc_controller.query_command(':MEASure:RJDJ:ALL?')
                RJ = round(float(RJDJALL.split(',')[4]) * 1e12, 2)
                print(f'C2C_jitter = {C2C_jitter}, Period_jitter = {Period_jitter}, RJ = {RJ}')
                current_time = datetime.now()
                formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
                result = [formatted_time, self.chip_id, self.voltcorner, self.temp, hex(probe_clk0_div), hex(p19v33_ds),
                          freq, C2C_jitter, Period_jitter, RJ]
                self.write_to_csv([result], './report/ATC001_XCLK_Freq.csv', self.report_header)
                osc_controller.save_image(
                    self.image_path_osc + f'test_ATC001_{self.chip_id}#@A03_XCLK_{freq}M_DS{p19v33_ds}_Jitter_{self.temp}+{self.voltcorner}')
                # input("Press Enter to continue...")
        osc_controller.disconnect()


if __name__ == "__main__":
    test = EVtest_XCLK_Freq()
    test.run()
