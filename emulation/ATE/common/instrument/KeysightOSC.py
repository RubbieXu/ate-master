import pyvisa


class OscilloscopeController:
    def __init__(self, instrument_address):
        self.rm = pyvisa.ResourceManager()
        self.osc = None
        self.instrument_address = instrument_address

    def connect(self):
        try:
            # 打开连接
            self.osc = self.rm.open_resource(f'TCPIP0::{self.instrument_address}::INSTR')
            # 设置超时时间，单位为毫秒
            self.osc.timeout = 5000
            print("成功连接到示波器")
        except Exception as e:
            print("连接示波器时出现错误:", e)

    def query_command(self, command):
        if self.osc is None:
            print("请先连接示波器")
            return
        try:
            # 发送命令
            response = self.osc.query(command)
            print(command)
            print("示波器响应:", response)
            return response
        except Exception as e:
            print("发送命令时出现错误:", e)

    def send_command(self, command):
        if self.osc is None:
            print("请先连接示波器")
            return
        try:
            # 发送写入命令
            self.osc.write(command)
            print(command)
        except Exception as e:
            print("发送写入命令时出现错误:", e)

    def save_image(self, file_name, format='PNG',save_setup='OFF'):
        self.send_command(f':DISK:SAVE:IMAGe "{file_name}",{format},SCReen,OFF,NORMal,{save_setup}')

    def load_setup(self, setup_name):
        self.send_command(f':DISK:LOAD "{setup_name}"')

    def disconnect(self):
        if self.osc is not None:
            self.osc.close()
            print("已断开示波器连接")
        self.rm.close()


if __name__ == "__main__":
    # 假设示波器的 VISA 地址是 'TCPIP0::192.168.1.100::INSTR'，根据实际情况修改
    osc_controller = OscilloscopeController('192.168.1.100')
    osc_controller.connect()
    # 发送一个简单的查询命令，例如 *IDN? 用于查询设备的身份信息
    osc_controller.query_command('*IDN?')
    # 发送一个设置命令，例如设置通道 1 的垂直刻度为 1V/div，根据示波器的命令集修改
    osc_controller.send_command('CHAN1:SCALE 1.0')
    osc_controller.disconnect()